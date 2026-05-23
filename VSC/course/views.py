from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Course, CourseEnrollment
from task.models import Submission


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    modules = course.modules.all().prefetch_related('tasks__task')

    is_enrolled = False
    solved_task_ids = []

    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(
            user=request.user,
            course=course
        ).exists()

        # ID задач, решённых пользователем
        solved_task_ids = Submission.objects.filter(
            user=request.user,
            status__name='Accepted',
            task__coursetask__module__course=course
        ).values_list('task_id', flat=True).distinct()

    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'solved_task_ids': list(solved_task_ids),
    }
    return render(request, 'course/course_detail.html', context)


@login_required
def enroll_course(request, pk):
    """Запись на курс."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    course = get_object_or_404(Course, pk=pk)

    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        return JsonResponse({'success': True, 'message': 'Вы записаны на курс!'})
    else:
        return JsonResponse({'success': True, 'message': 'Вы уже записаны на этот курс'})
