from django.shortcuts import render

def task_detail(request, pk):
    context = {
        'task_id': pk,
    }
    return render(request, 'task/task_detail.html', context)