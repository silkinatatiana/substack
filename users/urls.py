from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('chats/', views.chats_view, name='chats'),
    path('profile/<int:pk>/info/', views.user_profile_view, name='user_profile'),
]
