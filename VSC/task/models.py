from django.db import models
from django.conf import settings


# ==========================================
# 1. ТАБЛИЦЫ-СПРАВОЧНИКИ (Для нормализации)
# ==========================================

class Difficulty(models.Model):
    """Справочник сложности для начисления очков."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Сложность")
    base_points = models.IntegerField(default=100, verbose_name="Базовые очки (XP)")

    class Meta:
        verbose_name = "Уровень сложности"
        verbose_name_plural = "Уровни сложности"

    def __str__(self):
        return f"{self.name} ({self.base_points} XP)"


class ProgrammingLanguage(models.Model):
    """Справочник языков программирования."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Язык")

    class Meta:
        verbose_name = "Язык программирования"
        verbose_name_plural = "Языки программирования"

    def __str__(self):
        return self.name


class SubmissionStatus(models.Model):
    """Справочник статусов решения (Accepted, Wrong Answer и т.д.)."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Статус")

    class Meta:
        verbose_name = "Статус решения"
        verbose_name_plural = "Статусы решений"

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категории задач (Алгоритмы, Массивы и т.д.)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


# ==========================================
# 2. ОСНОВНЫЕ МОДЕЛИ БЛОКА ЗАДАЧ
# ==========================================

class Task(models.Model):
    """Основная модель задачи."""
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")

    # НОРМАЛИЗАЦИЯ: Связи через ForeignKey и ManyToMany
    difficulty = models.ForeignKey(
        Difficulty,
        on_delete=models.PROTECT,
        verbose_name="Сложность"
    )
    categories = models.ManyToManyField(
        Category,
        related_name='tasks',
        verbose_name="Категории"
    )
    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.PROTECT,
        verbose_name="Целевой язык"
    )

    starter_code = models.TextField(blank=True, null=True, verbose_name="Начальный код")
    solution_code = models.TextField(blank=True, null=True, verbose_name="Эталонное решение")

    time_limit_ms = models.IntegerField(default=1000, verbose_name="Лимит времени (мс)")
    memory_limit_kb = models.IntegerField(default=256000, verbose_name="Лимит памяти (КБ)")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name="Автор"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.difficulty.name})"


class TestCase(models.Model):
    """Тестовые данные для автоматической проверки решения."""
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='test_cases',
        verbose_name="Задача"
    )
    input_data = models.TextField(verbose_name="Входные данные")
    expected_output = models.TextField(verbose_name="Ожидаемый вывод")
    is_hidden = models.BooleanField(default=False, verbose_name="Скрытый тест")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Тестовый случай"
        verbose_name_plural = "Тестовые случаи"
        ordering = ['order']

    def __str__(self):
        return f"Тест для {self.task.title} (ID: {self.id})"


# ==========================================
# 3. User-related модели
# ==========================================

class Submission(models.Model):
    """Решение задачи пользователем."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_solutions',
        verbose_name="Пользователь"
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='solutions',
        verbose_name="Задача"
    )

    # НОРМАЛИЗАЦИЯ: Статус вынесен в справочник
    status = models.ForeignKey(
        SubmissionStatus,
        on_delete=models.PROTECT,
        verbose_name="Статус"
    )

    code = models.TextField(verbose_name="Код решения")
    execution_time_ms = models.IntegerField(null=True, blank=True, verbose_name="Время выполнения")
    memory_used_kb = models.IntegerField(null=True, blank=True, verbose_name="Память (КБ)")

    solved_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата решения")

    class Meta:
        verbose_name = "Решение задачи"
        verbose_name_plural = "Решения задач"
        ordering = ['-solved_at']

    def __str__(self):
        return f"{self.user.username} — {self.task.title} ({self.status.name})"


class PublishedSolution(models.Model):
    """Опубликованное эталонное решение."""
    submission = models.ForeignKey(
        'Submission',
        on_delete=models.CASCADE,
        related_name='published',
        verbose_name='Решение'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='published_solutions',
        verbose_name='Автор'
    )
    description = models.TextField(blank=True, default='', verbose_name='Описание решения')
    upvotes = models.IntegerField(default=0, verbose_name='Голоса')
    published_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Опубликованное решение'
        verbose_name_plural = 'Опубликованные решения'
        db_table = 'published_solutions'

    def __str__(self):
        return f'Решение от {self.author.username} к {self.submission.task.title}'


class SolutionVote(models.Model):
    """Лайк/дизлайк опубликованного решения."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solution_votes'
    )
    solution = models.ForeignKey(
        'PublishedSolution',
        on_delete=models.CASCADE,
        related_name='votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Голос за решение'
        verbose_name_plural = 'Голоса за решения'
        unique_together = ('user', 'solution')

    def str(self):
        return f'{self.user.username} → {self.solution.id}'


class Comment(models.Model):
    """Комментарий к задаче или решению."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    task = models.ForeignKey(
        'Task',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name='Задача'
    )
    solution = models.ForeignKey(
        'PublishedSolution',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name='Решение'
    )
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        db_table = 'comments'

    def __str__(self):
        if self.task:
            return f'Комментарий от {self.user.username} к задаче {self.task.title}'
        return f'Комментарий от {self.user.username} к решению'
