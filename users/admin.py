from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class UserAdminCustom(UserAdmin):
    list_display = [
        'username',
        'email',
        'bio',
        'is_author',
        'created_at',
        'monetizations',
        'price_month',
        'free_subscribers_count',
        'paid_subscribers_count',
    ]
    list_filter = ['is_author', 'monetizations']
    search_fields = ['username', 'email']
    ordering = ['-created_at']

    @admin.display(description="Free subscribers")
    def free_subscribers_count(self, obj):
        return obj.free_subscribers_count

    @admin.display(description="Paid subscribers")
    def paid_subscribers_count(self, obj):
        return obj.paid_subscribers_count