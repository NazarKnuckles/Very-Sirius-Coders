from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Achievement, UserAchievement


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'level', 'experience_points', 'created_at', 'is_staff')
    list_filter = ('level', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('email',)}),
        ('Игровая статистика', {'fields': ('level', 'experience_points')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Даты', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )

    readonly_fields = ('created_at',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement', 'earned_at')
    search_fields = ('user__username', 'achievement__name')
    raw_id_fields = ('user', 'achievement')
