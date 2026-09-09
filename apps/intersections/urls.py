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
        views.UpdateCommentView.as_view(),
        name='comment-edit'
    ),
    path(
        'comment/<int:pk>/like/',
        views.LikeCommentView.as_view(),
        name='comment-like'
    ),
    path(
        'comment/<int:pk>/unlike/',
        views.UnlikeCommentView.as_view(),
        name='comment-unlike'
    ),
    path(
        'comment/<int:pk>/answer/',
        views.CreateCommentAnswerView.as_view(),
        name='answer-create'
    ),
    path(
        'answer/<int:pk>/edit/',
        views.UpdateCommentAnswerView.as_view(),
        name='answer-edit'
    ),
    path(
        'answer/<int:pk>/delete/',
        views.RemoveCommentAnswerView.as_view(),
        name='answer-delete'
    ),
    ]