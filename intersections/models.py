from django.db import models
from django.urls import reverse

from posts.models import Post
from substack_app import settings
from users.models import TimeStampedModel


class Like(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes',
                             verbose_name='Лайки')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='Комментарии')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Посты')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments',
                             verbose_name='Пользователи')
    text = models.TextField(max_length=255, verbose_name='Текст комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']