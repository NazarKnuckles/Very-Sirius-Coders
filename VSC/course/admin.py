from django.contrib import admin
from .models import Course, CourseModule, CourseTask, CourseEnrollment


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title',)
    raw_id_fields = ('author',)
    inlines = [CourseModuleInline]


class CourseTaskInline(admin.TabularInline):
    model = CourseTask
    extra = 1
    raw_id_fields = ('task',)


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order_index')
    list_filter = ('course',)
    raw_id_fields = ('course',)
    inlines = [CourseTaskInline]


@admin.register(CourseTask)
class CourseTaskAdmin(admin.ModelAdmin):
    list_display = ('module', 'task', 'order_index')
    raw_id_fields = ('module', 'task')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percent', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    raw_id_fields = ('user', 'course')