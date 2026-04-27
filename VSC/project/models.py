from django.db import models
from users.models import User


class ProjectStatus(models.Model):
    """Статусы проекта: Идея, В разработке, Завершён."""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Статус проекта'
        verbose_name_plural = 'Статусы проектов'

    def __str__(self):
        return self.name


class Role(models.Model):
    """Роли участников: Backend, Frontend, Team Lead, QA."""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class Project(models.Model):
    """Проект."""
    title = models.CharField(max_length=150, verbose_name='Название')
    description = models.TextField(blank=True, default='', verbose_name='Описание')
    status = models.ForeignKey(
        ProjectStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name='Статус'
    )
    repository_url = models.CharField(max_length=255, blank=True, default='', verbose_name='Ссылка на репозиторий')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_projects',
        verbose_name='Создатель'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.title


class ProjectMember(models.Model):
    """Участник проекта с указанием роли."""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Проект'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_memberships',
        verbose_name='Пользователь'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='Роль'
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата вступления')

    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'
        unique_together = ('project', 'user')  # один пользователь — один раз в проекте

    def __str__(self):
        return f'{self.user.username} → {self.project.title} ({self.role})'


class ProjectVacancy(models.Model):
    """Открытая вакансия в проекте."""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='vacancies',
        verbose_name='Проект'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='vacancies',
        verbose_name='Роль'
    )
    description = models.TextField(blank=True, default='', verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Вакансия проекта'
        verbose_name_plural = 'Вакансии проектов'

    def __str__(self):
        return f'{self.role.name} → {self.project.title}'