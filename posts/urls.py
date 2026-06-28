from django.urls import path

from . import views


app_name = 'posts'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('new/', views.post_create, name='create'),
    path('<int:pk>/', views.PostDetail.as_view(), name='detail'),
    path('<int:pk>/edit/', views.post_update, name='update'),
    path('<int:pk>/delete/', views.post_delete, name='delete'),
    path('<int:pk>/image/change/', views.change_image_view, name='change_image'),
]