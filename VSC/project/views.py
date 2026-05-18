from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Project, ProjectMember, ProjectVacancy, ProjectStatus, Role


# ==========================================
# ПРОЕКТЫ
# ==========================================

class ProjectListView(ListView):
    """Список всех проектов на платформе."""
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # Подтягиваем статус и создателя одним запросом, сортируем от новых к старым
        return Project.objects.select_related('status', 'created_by').all().order_by('-created_at')


class ProjectDetailView(DetailView):
    """Детальная страница проекта: участники и вакансии."""
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        # Подтягиваем команду проекта через related_name='members'
        context['members'] = project.members.select_related('user', 'role').all()

        # Подтягиваем только активные вакансии через related_name='vacancies'
        context['vacancies'] = project.vacancies.filter(is_active=True).select_related('role')

        # Проверяем, состоит ли текущий юзер в этом проекте
        if self.request.user.is_authenticated:
            context['is_member'] = project.members.filter(user=self.request.user).exists()
        else:
            context['is_member'] = False

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Создание нового проекта."""
    model = Project
    fields = ['title', 'description', 'repository_url']
    template_name = 'projects/project_form.html'

    def form_valid(self, form):
        project = form.save(commit=False)
        project.created_by = self.request.user

        # Автоматически назначаем статус "Идея" при создании
        default_status, _ = ProjectStatus.objects.get_or_create(name='Идея')
        project.status = default_status
        project.save()

        # Добавляем создателя в участники с ролью "Team Lead"
        lead_role, _ = Role.objects.get_or_create(name='Team Lead')
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=lead_role
        )

        return redirect('project_detail', pk=project.pk)


# ==========================================
# ВАКАНСИИ И ОТКЛИКИ
# ==========================================

class VacancyListView(ListView):
    """Глобальная доска открытых вакансий по всем проектам."""
    model = ProjectVacancy
    template_name = 'projects/vacancy_list.html'
    context_object_name = 'vacancies'

    def get_queryset(self):
        return ProjectVacancy.objects.filter(is_active=True).select_related('project', 'role')


class VacancyCreateView(LoginRequiredMixin, CreateView):
    """Создание новой вакансии внутри проекта."""
    model = ProjectVacancy
    fields = ['role', 'description']
    template_name = 'projects/vacancy_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])

        # Защита: вакансии может открывать только участник проекта
        if not project.members.filter(user=self.request.user).exists():
            messages.error(self.request, "Только участники команды могут открывать вакансии.")
            return redirect('project_detail', pk=project.pk)

        vacancy = form.save(commit=False)
        vacancy.project = project
        vacancy.save()

        return redirect('project_detail', pk=project.pk)


class ApplyVacancyView(LoginRequiredMixin, View):
    """Логика отклика на вакансию и вступления в проект."""

    def post(self, request, vacancy_id):
        vacancy = get_object_or_404(ProjectVacancy, pk=vacancy_id, is_active=True)
        project = vacancy.project

        # Защита от дублирования: проверка на существование записи в ProjectMember
        if project.members.filter(user=request.user).exists():
            messages.warning(request, "Вы уже состоите в этом проекте.")
            return redirect('project_detail', pk=project.pk)

        # Создаем запись участника
        ProjectMember.objects.create(
            project=project,
            user=request.user,
            role=vacancy.role
        )

        # Закрываем вакансию
        vacancy.is_active = False
        vacancy.save()

        messages.success(request, f"Вы успешно присоединились к проекту на роль {vacancy.role.name}!")
        return redirect('project_detail', pk=project.pk)
