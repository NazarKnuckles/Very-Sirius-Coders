from django.contrib import admin
from .models import ProjectStatus, Role, Project, ProjectMember, ProjectVacancy, CourseModule, CourseLesson

@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0
    raw_id_fields = ('user',)

class ProjectVacancyInline(admin.TabularInline):
    model = ProjectVacancy
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'created_by__username')
    raw_id_fields = ('created_by',)
    inlines = [ProjectMemberInline, ProjectVacancyInline]

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__username', 'project__title')
    raw_id_fields = ('user', 'project')

@admin.register(ProjectVacancy)
class ProjectVacancyAdmin(admin.ModelAdmin):
    list_display = ('project', 'role', 'is_active')
    list_filter = ('is_active', 'role')
    search_fields = ('project__title',)
    raw_id_fields = ('project',)

admin.site.register(CourseModule)
admin.site.register(CourseLesson)