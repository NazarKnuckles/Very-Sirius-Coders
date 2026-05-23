from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('<int:pk>/', views.course_detail, name='detail'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll'),
]