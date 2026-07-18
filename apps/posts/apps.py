from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PostsConfig(AppConfig):
    name = 'apps.posts'
    verbose_name = _('Посты')
    # сделать тоже самое для всех остальных приложений