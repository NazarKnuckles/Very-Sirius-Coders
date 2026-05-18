from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('<int:pk>/', views.course_detail, name='detail'),
]