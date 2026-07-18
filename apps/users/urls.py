from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/info/', views.profile_view, name='profile'), # Todo переписать все на cbv и объединить эту ручку со следующей
    path('avatar/change/', views.change_avatar_view, name='change_avatar'),

]
