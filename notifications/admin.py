from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['type', 'user', 'post', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['text', 'user__username']
    autocomplete_fields = ['user', 'post']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
