from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile'),
    path('portfolio/', views.UserPortfolioView.as_view(), name='portfolio'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),
    path('achievements/', views.AchievementListView.as_view(), name='achievements'),
]