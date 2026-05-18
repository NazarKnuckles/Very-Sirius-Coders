from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Task, PublishedSolution
from .models import SolutionVote
from .models import Comment


def task_detail(request, pk):
    """Детальная страница задачи."""
    task = get_object_or_404(Task, pk=pk, is_active=True)
    test_cases = task.test_cases.filter(is_hidden=False)
    user_has_published = False
    if request.user.is_authenticated:
        user_has_published = PublishedSolution.objects.filter(
            submission__user=request.user,
            submission__task=task
        ).exists()

    context = {
        'task': task,
        'test_cases': test_cases,
        'user_has_published': user_has_published,
    }
    return render(request, 'task/task_detail.html', context)


def published_solutions(request, pk):
    task = get_object_or_404(Task, pk=pk)
    solutions_list = PublishedSolution.objects.filter(
        submission__task=task
    ).select_related('author', 'submission__user').order_by('-published_at')

    paginator = Paginator(solutions_list, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    voted_ids = []
    if request.user.is_authenticated:
        voted_ids = SolutionVote.objects.filter(
            user=request.user,
            solution__in=page_obj.object_list
        ).values_list('solution_id', flat=True)

    # Подсчёт комментариев для каждого решения
    solution_ids = [s.id for s in page_obj.object_list]
    comment_counts = {}
    if solution_ids:
        from django.db.models import Count
        counts = Comment.objects.filter(
            solution_id__in=solution_ids
        ).values('solution_id').annotate(count=Count('id'))
        comment_counts = {c['solution_id']: c['count'] for c in counts}

    context = {
        'task': task,
        'solutions': page_obj,
        'page_obj': page_obj,
        'voted_ids': list(voted_ids),
        'comment_counts': comment_counts,
    }
    return render(request, 'task/solutions.html', context)


@login_required
def publish_solution(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    task = get_object_or_404(Task, pk=pk)
    code = request.POST.get('code', '')

    if not code.strip():
        return JsonResponse({'error': 'Пустой код'}, status=400)
    existing = PublishedSolution.objects.filter(
        submission__user=request.user,
        submission__task=task,
        submission__code=code
    ).exists()

    if existing:
        return JsonResponse({'error': 'Решение уже опубликовано'}, status=400)

    from .models import Submission, SubmissionStatus
    status, _ = SubmissionStatus.objects.get_or_create(name='Published')

    submission = Submission.objects.create(
        user=request.user,
        task=task,
        status=status,
        code=code
    )

    PublishedSolution.objects.create(
        submission=submission,
        author=request.user
    )

    return JsonResponse({'success': True, 'message': 'Решение опубликовано'})


@login_required
def save_solution(request, pk):
    """Сохраняет решение пользователя при тесте/запуске."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    task = get_object_or_404(Task, pk=pk)
    code = request.POST.get('code', '')
    status_name = request.POST.get('status', 'Accepted')

    from .models import Submission, SubmissionStatus
    status, _ = SubmissionStatus.objects.get_or_create(name=status_name)

    submission, created = Submission.objects.update_or_create(
        user=request.user,
        task=task,
        defaults={
            'code': code,
            'status': status,
            'execution_time_ms': 100,  # мок
            'memory_used_kb': 1024,  # мок
        }
    )

    return JsonResponse({'success': True, 'message': 'Решение сохранено'})


@login_required
@require_POST
def toggle_vote(request, solution_pk):
    solution = get_object_or_404(PublishedSolution, pk=solution_pk)
    vote, created = SolutionVote.objects.get_or_create(
        user=request.user,
        solution=solution
    )
    if not created:
        vote.delete()
        solution.upvotes -= 1
        solution.save()
        return JsonResponse({
            'success': True,
            'action': 'removed',
            'upvotes': solution.upvotes
        })
    solution.upvotes += 1
    solution.save()
    return JsonResponse({
        'success': True,
        'action': 'added',
        'upvotes': solution.upvotes
    })


@login_required
@require_POST
def add_comment(request, solution_pk):
    """Добавление комментария к решению."""
    solution = get_object_or_404(PublishedSolution, pk=solution_pk)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Комментарий не может быть пустым'}, status=400)
    if len(content) > 1000:
        return JsonResponse({'error': 'Максимум 1000 символов'}, status=400)

    comment = Comment.objects.create(
        user=request.user,
        solution=solution,
        content=content
    )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'author': comment.user.username,
            'content': comment.content,
            'date': comment.created_at.strftime('%d.%m.%Y %H:%M'),
        }
    })


def solution_comments(request, solution_pk):
    """Страница одного решения со всеми комментариями."""
    solution = get_object_or_404(PublishedSolution.objects.select_related(
        'author', 'submission__user', 'submission__task'
    ), pk=solution_pk)

    comments_list = Comment.objects.filter(solution=solution).select_related('user').order_by('created_at')

    paginator = Paginator(comments_list, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Лайк
    voted = False
    if request.user.is_authenticated:
        voted = SolutionVote.objects.filter(user=request.user, solution=solution).exists()

    context = {
        'solution': solution,
        'comments': page_obj,
        'page_obj': page_obj,
        'voted': voted,
        'is_single_view': True,
    }
    return render(request, 'task/solution_detail.html', context)


def load_comments(request, solution_pk):
    solution = get_object_or_404(PublishedSolution, pk=solution_pk)
    offset = int(request.GET.get('offset', 0))
    limit = 5  # максимум 5 за раз

    comments = Comment.objects.filter(
        solution=solution
    ).select_related('user').order_by('created_at')[offset:offset + limit]

    total = Comment.objects.filter(solution=solution).count()

    data = [{
        'id': c.id,
        'author': c.user.username,
        'content': c.content,
        'date': c.created_at.strftime('%d.%m.%Y %H:%M'),
    } for c in comments]

    return JsonResponse({
        'comments': data,
        'total': total,
        'has_more': (offset + limit) < total,
        'offset': offset
    })
