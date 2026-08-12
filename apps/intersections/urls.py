from django.urls import path

from . import views

app_name = 'intersections'

urlpatterns = [
    path(
        'post/<int:pk>/like/',
        views.LikeView.as_view(),
        name='like',
    ),
    path(
        'post/<int:pk>/unlike/',
        views.UnlikeView.as_view(),
        name='unlike',
    ),
    path(
        'post/<int:pk>/likes/',
        views.LikeListView.as_view(),
        name='likes',
    ),
]
