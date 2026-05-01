from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from intersections.models import Comment
from .models import Post


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ['user', 'text_preview', 'created_at', 'view_comment_link']
    readonly_fields = ['text_preview', 'created_at', 'view_comment_link']
    ordering = ['-created_at']

    def text_preview(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text

    text_preview.short_description = 'Текст комментария'

    def view_comment_link(self, obj):
        if obj and obj.pk:
            return format_html(
                '<a href="/admin/intersections/comment/{}/change/">🔗 Открыть комментарий</a>',
                obj.pk
            )
        return '-'

    view_comment_link.short_description = 'Переход к комментарию'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'visibility',
                    'likes_count', 'comments_count', 'created_at']
    list_filter = ['is_published', 'visibility', 'created_at', 'author']
    search_fields = ['title', 'text']
    raw_id_fields = ['author']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    inlines = [CommentInline]

    def likes_count(self, obj):
        return obj.likes.count()

    likes_count.short_description = 'Лайки'
    likes_count.admin_order_field = 'likes__count'

    def comments_count(self, obj):
        return obj.comments.count()

    comments_count.short_description = 'Комментарии'
    comments_count.admin_order_field = 'comments__count'
