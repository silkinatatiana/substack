from django.db import models

from apps.posts.models import Post
from substack_app import settings
from apps.users.models import TimeStampedModel


class LikePost(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_likes',
        verbose_name='Пользователь',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пост',
    )

    class Meta:
        verbose_name = 'Лайк поста'
        verbose_name_plural = 'Лайки постов'
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_post_like'),
        ]


class Comment(TimeStampedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пользователь',
    )
    text = models.TextField(max_length=255, verbose_name='Текст комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']


class CommentAnswer(TimeStampedModel):
    parent_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Комментарий',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_answers',
        verbose_name='Пользователь',
    )
    text = models.TextField(max_length=255, verbose_name='Текст ответа')

    class Meta:
        verbose_name = 'Ответ на комментарий'
        verbose_name_plural = 'Ответы на комментарии'
        ordering = ['-created_at']


class LikeComment(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes',
        verbose_name='Пользователь',
    )
    comment = models.ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Комментарий',
    )
    comment_answer = models.ForeignKey(
        CommentAnswer,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Ответ на комментарий',
    )

    class Meta:
        verbose_name = 'Лайк комментария'
        verbose_name_plural = 'Лайки комментариев'
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(comment__isnull=False, comment_answer__isnull=True)
                    | models.Q(comment__isnull=True, comment_answer__isnull=False)
                ),
                name='like_comment_exactly_one_target',
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_comment_like',
            ),
            models.UniqueConstraint(
                fields=['user', 'comment_answer'],
                condition=models.Q(comment_answer__isnull=False),
                name='unique_comment_answer_like',
            ),
        ]
