from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from substack_app import settings
from users.models import TimeStampedModel


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=96, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'category'
            candidate = base
            n = 2
            while Category.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{n}'
                n += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class Post(TimeStampedModel):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "Все"
        PUBLIC_AUTH = "public_auth", "Авторизованные пользователи"
        SUBSCRIBERS = "subscribers", "Только подписчики"
        PAID = "paid", "Только платные подписчики"
        DRAFT = "draft", "Только я (черновик)"

    title = models.CharField(max_length=50, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст поста')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts',
                               verbose_name='Автор')
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC,
                                  verbose_name='Видимость поста')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='posts',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['author', 'created_at'],
                name='posts_post_author_created_idx',
            ),
            models.Index(
                fields=['category', 'created_at'],
                name='posts_post_cat_created_idx',
            ),
        ]

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.title} {self.author}"


class PostImage(TimeStampedModel):
    image = models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='Изображение')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name='Пост')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['-created_at']

    def __str__(self):
        return f"Изображение для {self.post}"