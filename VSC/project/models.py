from django.db import models
from users.models import User

class ProjectStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Статус проекта'
        verbose_name_plural = 'Статусы проектов'

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')
    description = models.TextField(blank=True, default='', verbose_name='Описание')
    status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Статус')
    repository_url = models.CharField(max_length=255, blank=True, default='', verbose_name='Ссылка на репозиторий')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_course = models.BooleanField(default=False, verbose_name='Это учебный курс')
    tech_stack = models.CharField(max_length=255, blank=True, verbose_name='Стек технологий')
    budget_xp = models.PositiveIntegerField(default=0, verbose_name='Награда за участие (XP)')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.title

class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Проект')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Роль')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата вступления')

    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'
        unique_together = ('project', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.project.title}'

class ProjectVacancy(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Проект')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль')
    description = models.TextField(blank=True, default='', verbose_name='Описание требований')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Вакансия проекта'
        verbose_name_plural = 'Вакансии проектов'

    def __str__(self):
        return f'{self.role.name} - {self.project.title}'

class Application(models.Model):
    vacancy = models.ForeignKey(ProjectVacancy, on_delete=models.CASCADE, verbose_name='Вакансия')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Кандидат')
    text = models.TextField(verbose_name='Сопроводительное письмо')
    status = models.CharField(max_length=20, default='Ожидает', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        unique_together = ('vacancy', 'user')

    def __str__(self):
        return f'{self.user.username} на {self.vacancy.role.name}'

# Добавь этот код в самый низ файла project/models.py

class CourseModule(models.Model):
    """Модуль (Глава) курса"""
    course = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField('Название модуля', max_length=200)
    order = models.PositiveIntegerField('Порядок (номер)', default=1)

    class Meta:
        verbose_name = 'Модуль курса'
        verbose_name_plural = 'Модули курсов'
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Модуль {self.order}: {self.title}"

class CourseLesson(models.Model):
    """Урок внутри модуля (теория или задача)"""
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField('Тема урока', max_length=200)
    content = models.TextField('Материал урока (теория)', blank=True)
    
    # Сюда позже можно будет прикрепить файл, видео или связать с приложением Task
    # task = models.ForeignKey('task.Task', on_delete=models.SET_NULL, null=True, blank=True)
    
    order = models.PositiveIntegerField('Порядок (номер)', default=1)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - Урок {self.order}: {self.title}"