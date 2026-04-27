from django.db import models
from django.conf import settings

class Course(models.Model):
    """Основные данные учебного курса."""
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание курса")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_courses',
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class CourseModule(models.Model):
    """Разделы или недели внутри курса."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name="Курс"
    )
    title = models.CharField(max_length=200, verbose_name="Название модуля")
    order_index = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Модуль курса"
        verbose_name_plural = "Модули курсов"
        ordering = ['order_index']

    def __str__(self):
        return f"{self.course.title} — {self.title}"

class CourseTask(models.Model):
    """Связующая таблица: какие задачи из банка входят в модуль."""
    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Модуль"
    )
    # Ссылка на модель Task из другого приложения
    task = models.ForeignKey(
        'task.Task',
        on_delete=models.CASCADE,
        verbose_name="Задача из банка"
    )
    order_index = models.PositiveIntegerField(default=0, verbose_name="Порядок задачи в модуле")

    class Meta:
        verbose_name = "Задача курса"
        verbose_name_plural = "Задачи курсов"
        ordering = ['order_index']

    def __str__(self):
        return f"{self.module.title} — {self.task.title}"

class CourseEnrollment(models.Model):
    """Запись пользователя на курс и его прогресс."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Студент"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name="Курс"
    )
    progress_percent = models.IntegerField(default=0, verbose_name="Процент выполнения")
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата записи")

    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        unique_together = ('user', 'course') # Чтобы нельзя было записаться дважды

    def __str__(self):
        return f"{self.user.username} обучается на {self.course.title}"
