from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/edit/', views.UserUpdateView.as_view(), name='update'),
]
