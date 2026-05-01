from django.db import models
from django.urls import reverse

from users.models import User


class EmailSystem(models.Model):
    email = models.EmailField(max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_confirmed = models.BooleanField(default=False)
    subscribed_to_the_newsletter = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Email'

    def get_absolute_url(self):
        return reverse('user_email/', kwargs={})
