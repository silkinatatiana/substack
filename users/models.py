from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        abstract = True


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True, verbose_name='Имя пользователя')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Описание')
    avatar = models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватар')
    website_url = models.URLField(blank=True, max_length=40, verbose_name='Ссылка на сайт')
    tg_name = models.CharField(blank=True, max_length=20, verbose_name='Телеграм')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    monetizations = models.BooleanField(default=False, verbose_name='Монетизация')
    price_month = models.DecimalField(max_digits=3, decimal_places=1, default=5, verbose_name='Стоимость в месяц')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_absolute_url(self):
        return reverse('user_profile/', kwargs={})

    @property
    def free_subscribers_count(self):
        from subscriptions.models import Subscription

        return self.subscribers.filter(tier=Subscription.Tier.FREE).count()

    @property
    def paid_subscribers_count(self):
        from subscriptions.models import Subscription

        return self.subscribers.filter(tier=Subscription.Tier.PAID).count()

    def __str__(self):
        return self.username

