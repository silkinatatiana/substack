from django.conf import settings
from django.db import models
from django.utils import timezone

from users.models import TimeStampedModel


class Subscription(TimeStampedModel):
    class Tier(models.TextChoices):
        FREE = "free", "Free"
        PAID = "paid", "Paid"

    subscriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions",
                                   verbose_name='Подписчики')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscribers", verbose_name='Автор')
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.FREE, verbose_name='Тариф')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "author"],
                name="unique_subscription",
            ),
            models.CheckConstraint(
                condition=~models.Q(subscriber=models.F("author")),
                name="no_self_subscription",
            ),
        ]

    def str(self):
        return f"{self.subscriber} -> {self.author} ({self.tier})"
