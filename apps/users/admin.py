from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.posts.models import Post
from apps.users.models import User


class PostInline(admin.TabularInline):
    model = Post
    fields = ['title', 'created_at']
    readonly_fields = ['title', 'created_at']
    extra = 0
    can_delete = True
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return True

# TODO оставить добавление поста в юзере, но открывать в модели поста

@admin.register(User)
class UserAdminCustom(UserAdmin):
    list_display = [
        'username',
        'email',
        'bio',
        'created_at',
        'monetizations',
        'price_month',
        'free_subscribers_count',
        'paid_subscribers_count',
        'count_posts_display',
    ]
    list_filter = ['monetizations']
    search_fields = ['username', 'email']
    ordering = ['-created_at']

    inlines = [PostInline]

    @admin.display(description="Free subscribers")
    def free_subscribers_count(self, obj):
        return obj.free_subscribers_count

    @admin.display(description="Paid subscribers")
    def paid_subscribers_count(self, obj):
        return obj.paid_subscribers_count

    @admin.display(description='Count posts')
    def count_posts_display(self, obj):
        return obj.posts_count