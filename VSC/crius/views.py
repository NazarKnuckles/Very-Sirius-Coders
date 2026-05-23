from django.shortcuts import render
from task.models import Task, Difficulty, Category
from course.models import Course
from course.models import CourseTask
from task.models import Task, Submission
from course.models import CourseEnrollment
from task.models import Task, Submission
from task.sandbox import run_in_sandbox

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

        submissions = Submission.objects.filter(
            user=request.user,
            task_id__in=solved_task_ids
        )

        solutions_dict = {}
        for sub in submissions:
            solutions_dict[sub.task_id] = {
                'status': sub.status.name,
                'passed': sub.passed_tests,
                'total': sub.total_tests,
            }
    else:
        tasks = Task.objects.none()
        solutions_dict = {}

    context = {
        'tasks': tasks,
        'solutions_dict': solutions_dict,
    }
    return render(request, 'crius/work_task_list.html', context)


def _count_passed_tests(submission):
    """Считает количество пройденных тестов для решения."""

    test_cases = submission.task.test_cases.all()
    passed = 0

    for tc in test_cases:
        result = run_in_sandbox(submission.code, tc.input_data)
        if result['success'] and result['output'].strip() == tc.expected_output.strip():
            passed += 1

    return passed


def work_course_list(request):
    if request.user.is_authenticated:
        # Только курсы, на которые записан пользователь
        enrolled_ids = CourseEnrollment.objects.filter(
            user=request.user
        ).values_list('course_id', flat=True)

        courses = Course.objects.filter(id__in=enrolled_ids).select_related('author')
    else:
        courses = Course.objects.none()

    # Прогресс для каждого курса (количество пройденных задач)
    progress_dict = {}
    if request.user.is_authenticated and courses:
        for course in courses:
            # Считаем количество задач в курсе
            total_tasks = CourseTask.objects.filter(
                module__course=course
            ).count()

            # Считаем решённые задачи из этого курса
            solved = Submission.objects.filter(
                user=request.user,
                status__name='Accepted',
                task__coursetask__module__course=course
            ).values('task').distinct().count()

            progress_dict[course.id] = {
                'solved': solved,
                'total': total_tasks,
            }

    context = {
        'courses': courses,
        'progress_dict': progress_dict,
    }
    return render(request, 'crius/work_course.html', context)

def work_project_list(request):
    return render(request, 'crius/work_project.html')
