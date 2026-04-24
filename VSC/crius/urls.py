from django.urls import path
from . import views

app_name = 'crius'

urlpatterns = [
    path('', views.basic_index, name='basic_index'),
    path('tasks/', views.task_list, name='list'),
    path('course/', views.course, name='course'),
    path('workspace/', views.workspace, name='workspace'),
    path('portfolio/', views.portfolio, name='portfolio'),
]
