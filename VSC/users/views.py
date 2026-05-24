from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from task.models import Submission
from course.models import CourseEnrollment
from project.models import ProjectMember
from .models import Achievement
from .forms import CustomUserCreationForm

User = get_user_model()


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')  # ← исправлено


class UserLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('users:portfolio')  # ← исправлено


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')  # ← исправлено


class UserProfileView(DetailView):
    """Публичный профиль любого пользователя."""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        accepted = Submission.objects.filter(user=user, status__name='Accepted')
        context['solved_tasks_count'] = accepted.values('task').distinct().count()

        total_xp_dict = accepted.aggregate(total=Sum('task__difficulty__base_points'))
        total_xp = total_xp_dict['total'] or 0
        context['total_xp'] = total_xp
        context['current_level'] = (total_xp // 1000) + 1
        context['xp_to_next_level'] = 1000 - (total_xp % 1000)
        context['xp_percent'] = (total_xp % 1000) / 10

        context['user_projects'] = user.project_memberships.select_related('project', 'role')
        context['achievements'] = user.achievements.select_related('achievement').order_by('-earned_at')
        context['enrollments'] = user.enrollments.select_related('course').order_by('-enrolled_at')

        return context


class UserPortfolioView(LoginRequiredMixin, DetailView):
    """Личное портфолио текущего пользователя."""
    template_name = 'users/portfolio.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        accepted = Submission.objects.filter(user=user, status__name='Accepted')
        context['solved_tasks_count'] = accepted.values('task').distinct().count()

        total_xp_dict = accepted.aggregate(total=Sum('task__difficulty__base_points'))
        total_xp = total_xp_dict['total'] or 0
        context['total_xp'] = total_xp
        context['current_level'] = (total_xp // 1000) + 1
        context['xp_to_next_level'] = 1000 - (total_xp % 1000)
        context['xp_percent'] = (total_xp % 1000) / 10

        projects = ProjectMember.objects.filter(user=user).select_related('project', 'role')
        context['user_projects'] = projects
        context['achievements'] = user.achievements.select_related('achievement').order_by('-earned_at')
        context['enrollments'] = user.enrollments.select_related('course')

        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'users/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:portfolio')  # ← исправлено


class AchievementListView(ListView):
    model = Achievement
    template_name = 'users/achievements.html'
    context_object_name = 'achievements'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['earned_achievement_ids'] = self.request.user.achievements.values_list(
                'achievement_id', flat=True
            )
        else:
            context['earned_achievement_ids'] = []
        return context