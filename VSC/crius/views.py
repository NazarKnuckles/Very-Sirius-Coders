from django.shortcuts import render
from task.models import Task, Difficulty, Category
from course.models import Course
from task.models import Task, Submission
from project.models import Project
from project.models import Project, ProjectVacancy

def basic_index(request):
    return render(request, 'crius/base.html')

def task_list(request):
    """Список задач из БД."""
    tasks = Task.objects.filter(is_active=True).select_related('difficulty', 'language')
    return render(request, 'crius/task_list.html', {'tasks': tasks})

def course_list(request):
    """Список всех курсов (берем из универсальной таблицы Project)."""
    courses = Project.objects.filter(is_course=True).order_by('-created_at')
    return render(request, 'crius/course.html', {'courses': courses})


def workspace(request):
    return render(request, 'crius/workspace.html')

from project.models import ProjectMember # Добавь в импорты

def portfolio(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
        
    # Находим все проекты, где текущий пользователь является участником
    memberships = ProjectMember.objects.filter(user=request.user).select_related('project', 'project__status', 'role')
    
    active_projects = []
    completed_projects = []
    
    for m in memberships:
        # Проверяем статус проекта. Если статус 'Завершён' — отправляем в архив
        if m.project.status and m.project.status.name == 'Завершён':
            completed_projects.append(m)
        else:
            active_projects.append(m)

    return render(request, 'crius/portfolio.html', {
        'active_projects': active_projects,
        'completed_projects': completed_projects
    })  

def work_task_list(request):
    if request.user.is_authenticated:
        solved_task_ids = Submission.objects.filter(
            user=request.user
        ).values_list('task_id', flat=True).distinct()

        tasks = Task.objects.filter(
            id__in=solved_task_ids,
            is_active=True
        ).select_related('difficulty', 'language')

        user_solutions = Submission.objects.filter(
            user=request.user,
            task_id__in=solved_task_ids
        ).values('task_id', 'status__name')
        solutions_dict = {s['task_id']: s['status__name'] for s in user_solutions}
    else:
        tasks = Task.objects.none()
        solutions_dict = {}

    context = {
        'tasks': tasks,
        'solutions_dict': solutions_dict,
    }
    return render(request, 'crius/work_task_list.html', context)

def work_course_list(request):
    if request.user.is_authenticated:
        # Достаем курсы, которые создал только текущий юзер
        my_courses = Project.objects.filter(is_course=True, created_by=request.user).order_by('-created_at')
    else:
        my_courses = []
        
    return render(request, 'crius/work_course.html', {'courses': my_courses})

def work_project_list(request):
    """Список проектов для рабочего пространства"""
    # Все проекты платформы
    all_projects = Project.objects.filter(is_course=False).order_by('-created_at')
    
    # Только те проекты, которые создал текущий вошедший пользователь
    my_projects = Project.objects.filter(is_course=False, created_by=request.user).order_by('-created_at')
    
    # Все активные вакансии
    global_vacancies = ProjectVacancy.objects.filter(is_active=True).select_related('project', 'role')
    
    return render(request, 'crius/work_project.html', {
        'projects': all_projects,
        'my_projects': my_projects,
        'global_vacancies': global_vacancies
    })