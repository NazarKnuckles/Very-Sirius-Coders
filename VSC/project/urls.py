from django.urls import path
from . import views

urlpatterns = [
    # Создание проекта
    path('create/', views.create_project, name='project_create'),
    
    # Детальная страница
    path('<int:pk>/', views.project_detail, name='project_detail'),
    
    # Управление вакансиями и заявками
    path('<int:pk>/add-vacancy/', views.create_vacancy, name='create_vacancy'),
    path('vacancy/<int:vac_id>/apply/', views.apply_vacancy, name='apply_vacancy'),
    path('application/<int:app_id>/<str:action>/', views.process_application, name='process_application'),

    # НОВЫЕ ПУТИ ДЛЯ КОНСТРУКТОРА КУРСОВ
    path('<int:pk>/add-module/', views.add_module, name='add_module'),
    path('<int:pk>/add-lesson/', views.add_lesson, name='add_lesson'),
]