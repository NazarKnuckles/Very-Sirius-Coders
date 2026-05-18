from django.shortcuts import render
from task.models import Task, Difficulty, Category
from course.models import Course
from task.models import Task, Submission

def basic_index(request):
    return render(request, 'crius/base.html')  # или 'index.html', если вынесете приветствие

def task_list(request):
    """Список задач из БД."""
    tasks = Task.objects.filter(is_active=True).select_related('difficulty', 'language')
    return render(request, 'crius/task_list.html', {'tasks': tasks})

def course_list(request):
    """Список всех курсов."""
    courses = Course.objects.all().select_related('author')
    return render(request, 'crius/course.html', {'courses': courses})

def workspace(request):
    return render(request, 'crius/workspace.html')

def portfolio(request):
    return render(request, 'crius/portfolio.html')

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
    return render(request, 'crius/work_course.html')

def work_project_list(request):
    return render(request, 'crius/work_project.html')
