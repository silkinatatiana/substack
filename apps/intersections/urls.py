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
    path(
        'post/<int:pk>/comments/',
        views.CommentListView.as_view(),
        name='comments'
    ),
    path(
        'post/<int:pk>/comment/',
        views.CreateCommentView.as_view(),
        name='comment-create'
    ),
    path(
        'comment/<int:pk>/delete/',
        views.RemoveCommentView.as_view(),
        name='comment-delete'
    ),
    path(
        'comment/<int:pk>/edit/',
        views.RefactorCommentView.as_view(),
        name='comment-edit'
    ),
    ]
