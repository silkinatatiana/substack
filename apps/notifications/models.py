from django.db import models
from django.urls import reverse

from apps.posts.models import Post
from substack_app import settings
from apps.users.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Type(models.TextChoices):
        NEW_SUBSCRIBER = "new_subscriber", "New subscriber"
        NEW_LIKE = "new_like", "New like"
        NEW_COMMENT = "new_comment", "New comment"
        NEW_POST = "new_post", "New post"

    type = models.CharField(choices=Type.choices, verbose_name='Тема')
    text = models.TextField(verbose_name='Текс уведоления')
    image_url = models.URLField(verbose_name='Ссылка на изображение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', blank=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def get_absolute_url(self):
        return reverse('notification/', kwargs={})