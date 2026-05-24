from django.contrib import admin
from .models import (
    Difficulty, ProgrammingLanguage, SubmissionStatus, Category,
    Task, TestCase, Submission
)


@admin.register(Difficulty)
class DifficultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_points')


@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(SubmissionStatus)
class SubmissionStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'language', 'author', 'is_active', 'created_at')
    list_filter = ('difficulty', 'language', 'is_active', 'categories')
    search_fields = ('title', 'description')
    raw_id_fields = ('author',)
    filter_horizontal = ('categories',)
    inlines = [TestCaseInline]


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('task', 'is_hidden', 'order')
    list_filter = ('is_hidden',)
    raw_id_fields = ('task',)


@admin.register(Submission)
class UserTaskSolutionAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'status', 'execution_time_ms', 'solved_at')
    list_filter = ('status', 'solved_at')
    search_fields = ('user__username', 'task__title')
    raw_id_fields = ('user', 'task')