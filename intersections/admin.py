from django.contrib import admin

from .models import Comment, Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_filter = ("created_at",)
    autocomplete_fields = ("user", "post")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "short_body", "created_at")
    list_filter = ("created_at",)
    autocomplete_fields = ("user", "post")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Комментарий")
    def short_body(self, obj):
        return obj.text[:70]