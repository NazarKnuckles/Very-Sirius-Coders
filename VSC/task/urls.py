from django.urls import path
from . import views

app_name = 'task'

urlpatterns = [
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<int:pk>/solutions/', views.published_solutions, name='solutions'),
    path('<int:pk>/publish/', views.publish_solution, name='publish'),
    path('<int:pk>/save/', views.save_solution, name='save_solution'),
    path('solution/<int:solution_pk>/vote/', views.toggle_vote, name='toggle_vote'),
    path('solution/<int:solution_pk>/comments/', views.solution_comments, name='solution_comments'),
    path('solution/<int:solution_pk>/comment/add/', views.add_comment, name='add_comment'),
    path('solution/<int:solution_pk>/comments/load/', views.load_comments, name='load_comments'),
]