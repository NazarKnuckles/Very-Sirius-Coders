from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# ДОБАВЛЕНЫ CourseModule и CourseLesson в импорты ниже:
from .models import Project, ProjectVacancy, Application, ProjectStatus, Role, ProjectMember, CourseModule, CourseLesson
from django.contrib import messages

@login_required
def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        project_type = request.POST.get('project_type')
        tech_stack = request.POST.get('tech_stack')
        
        # Защита от пустых значений.
        # Если пришло 'course', значит это курс. Иначе - обычный проект.
        is_course = True if project_type == 'course' else False
        
        # Ставим статус по умолчанию
        status, _ = ProjectStatus.objects.get_or_create(name='Идея')
        
        # Создаем проект
        project = Project.objects.create(
            title=title,
            description=description,
            status=status,
            is_course=is_course,  # Вот тут сохраняется флаг курса!
            tech_stack=tech_stack,
            created_by=request.user
        )
        
        # Делаем создателя участником проекта с ролью "Тимлид"
        lead_role, _ = Role.objects.get_or_create(name='Тимлид')
        ProjectMember.objects.create(project=project, user=request.user, role=lead_role)
        
        return redirect('project_detail', pk=project.pk)
        
    return render(request, 'projects/project_form.html')

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    vacancies = ProjectVacancy.objects.filter(project=project, is_active=True)
    members = ProjectMember.objects.filter(project=project)
    
    is_lead = (request.user == project.created_by)
    pending_apps = []
    has_applied_to = []
    
    if request.user.is_authenticated:
        if is_lead:
            # Тимлид видит заявки на свои вакансии
            pending_apps = Application.objects.filter(vacancy__project=project, status='Ожидает')
        else:
            # Обычный юзер видит, куда он уже подал заявку
            has_applied_to = Application.objects.filter(
                user=request.user, vacancy__project=project
            ).values_list('vacancy_id', flat=True)

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'members': members,
        'vacancies': vacancies,
        'is_lead': is_lead,
        'pending_apps': pending_apps,
        'has_applied_to': has_applied_to
    })

@login_required
def create_vacancy(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.created_by and request.method == 'POST':
        role_name = request.POST.get('title')
        requirements = request.POST.get('requirements')
        
        role, _ = Role.objects.get_or_create(name=role_name)
        ProjectVacancy.objects.create(
            project=project,
            role=role,
            description=requirements
        )
    return redirect('project_detail', pk=pk)

@login_required(login_url='/users/login/')
def apply_vacancy(request, vac_id):
    vacancy = get_object_or_404(ProjectVacancy, pk=vac_id)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter', '').strip()
        
        # Создаем заявку только если текст не пустой
        if cover_letter:
            Application.objects.get_or_create(
                vacancy=vacancy,
                user=request.user,
                defaults={'text': cover_letter}
            )
            messages.success(request, 'Ваша заявка успешно отправлена!')
            
    # Возвращаем пользователя обратно на страницу проекта
    return redirect('project_detail', pk=vacancy.project.pk)

@login_required
def process_application(request, app_id, action):
    app = get_object_or_404(Application, pk=app_id)
    if request.user == app.vacancy.project.created_by:
        if action == 'accept':
            app.status = 'Принято'
            # Добавляем юзера в команду
            ProjectMember.objects.get_or_create(
                project=app.vacancy.project,
                user=app.user,
                defaults={'role': app.vacancy.role}
            )
            # Закрываем вакансию
            app.vacancy.is_active = False
            app.vacancy.save()
        else:
            app.status = 'Отказ'
        app.save()
    return redirect('project_detail', pk=app.vacancy.project.pk)

# --- НОВЫЕ ФУНКЦИИ ДЛЯ КОНСТРУКТОРА КУРСОВ ---

@login_required(login_url='/users/login/')
def add_module(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.created_by and request.method == 'POST':
        title = request.POST.get('title')
        order = request.POST.get('order', 1)
        if title:
            CourseModule.objects.create(course=project, title=title, order=order)
    return redirect('project_detail', pk=pk)

@login_required(login_url='/users/login/')
def add_lesson(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.created_by and request.method == 'POST':
        module_id = request.POST.get('module_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        order = request.POST.get('order', 1)
        
        if module_id and title:
            module = get_object_or_404(CourseModule, pk=module_id, course=project)
            CourseLesson.objects.create(module=module, title=title, content=content, order=order)
    return redirect('project_detail', pk=pk)