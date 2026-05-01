from django.db import models
from django.urls import reverse

from substack_app import settings
from users.models import TimeStampedModel


class Post(TimeStampedModel):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        SUBSCRIBERS = "subscribers", "Subscribers only"
        PAID = "paid", "Paid subscribers only"
        DRAFT = "draft", "Draft"

    title = models.CharField(max_length=50, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст поста')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts',
                               verbose_name='Автор')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC,
                                  verbose_name='Видимость поста')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['author', 'created_at'],
                name='posts_post_author_created_idx',
            ),
        ]

    def get_absolute_url(self):
        return reverse('post/', kwargs={})

    def __str__(self):
        return f"{self.title} {self.author}"
