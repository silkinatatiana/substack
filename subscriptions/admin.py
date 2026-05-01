from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "author", "tier", "created_at")
    list_filter = ("tier", "created_at")
    autocomplete_fields = ("subscriber", "author")
    readonly_fields = ("created_at", "updated_at")