from django.contrib import admin

from apps.email_systems.models import EmailSystem


@admin.register(EmailSystem)
class EmailSystemAdmin(admin.ModelAdmin):
    list_display = ['email', 'user', 'is_confirmed', 'subscribed_to_the_newsletter']
    list_filter = ['email', 'user', 'is_confirmed', 'subscribed_to_the_newsletter']
    search_fields = ['email', 'user']
    ordering = ['email']