from django.contrib import admin

from apps.private_messages.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text',  'sender', 'recipient', 'created_at', 'updated_at', 'status']
    list_filter = ['sender', 'recipient', 'status']
    search_fields = ['text', 'sender', 'recipient', 'status']
    ordering = ['-created_at']