from django.shortcuts import render

def basic_index(request):
    return render(request, 'crius/base.html')  # или 'index.html', если вынесете приветствие

def task_list(request):
    return render(request, 'crius/task_list.html')

def course(request):
    return render(request, 'crius/course.html')

def workspace(request):
    return render(request, 'crius/workspace.html')

def portfolio(request):
    return render(request, 'crius/portfolio.html')