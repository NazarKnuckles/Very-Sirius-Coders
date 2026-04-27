from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Расширенная модель пользователя с уровнем и опытом."""
    level = models.IntegerField(default=1, verbose_name='Уровень')
    experience_points = models.IntegerField(default=0, verbose_name='Очки опыта')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='Группы, к которым принадлежит пользователь.',
        verbose_name='Группы'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Права пользователя.',
        verbose_name='Права'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'

    def __str__(self):
        return self.username


class Achievement(models.Model):
    """Достижения, которые может получить пользователь."""
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, default='', verbose_name='Описание')
    icon_url = models.CharField(max_length=255, blank=True, default='', verbose_name='URL иконки')

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        db_table = 'achievements'

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Связь пользователя с полученными достижениями."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Пользователь'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Достижение'
    )
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения')

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        db_table = 'user_achievements'
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f'{self.user.username} — {self.achievement.name}'