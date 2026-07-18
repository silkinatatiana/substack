from django.db import models
from django.urls import reverse

from substack_app import settings


class MessageStatus(models.TextChoices):
    SENT = 'sent', 'Отправлено'
    DELETED = 'deleted', 'Удалено'
    ERROR = 'error', 'Ошибка'


class Message(models.Model):
    text = models.TextField(verbose_name='Текст сообщения')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages',
                               verbose_name='Отправитель')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages',
                                  verbose_name='Получатель')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=MessageStatus,
        default=MessageStatus.SENT,
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def get_absolute_url(self):
        return reverse('message/', kwargs={})
