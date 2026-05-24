from django.shortcuts import render, get_object_or_404
from .models import Course


def course_detail(request, pk):
    """Детальная страница курса с модулями и задачами."""
    course = get_object_or_404(Course, pk=pk)
    modules = course.modules.all().prefetch_related('tasks__task')

    context = {
        'course': course,
        'modules': modules,
    }
    return render(request, 'course/course_detail.html', context)
