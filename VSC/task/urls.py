from django.urls import path
from . import views

app_name = 'task'

urlpatterns = [
    path('<int:pk>/', views.task_detail, name='detail'),
]