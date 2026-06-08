from django.db.models import Q

from subscriptions.models import Subscription

from .models import Post


def _subscribed_author_ids(user):
    return Subscription.objects.filter(subscriber=user).values_list('author_id', flat=True)


def _paid_subscribed_author_ids(user):
    return Subscription.objects.filter(
        subscriber=user,
        tier=Subscription.Tier.PAID,
    ).values_list('author_id', flat=True)


def post_visible_filter(user):
    V = Post.Visibility
    if not user or not user.is_authenticated:
        return Q(visibility=V.PUBLIC)

    return (
        Q(visibility=V.PUBLIC)
        | Q(visibility=V.PUBLIC_AUTH)
        | Q(author=user)
        | Q(visibility=V.SUBSCRIBERS, author_id__in=_subscribed_author_ids(user))
        | Q(visibility=V.PAID, author_id__in=_paid_subscribed_author_ids(user))
    )


def user_can_view_post(user, post):
    if post.author_id == getattr(user, 'id', None):
        return True

    V = Post.Visibility
    if post.visibility == V.DRAFT:
        return False
    if post.visibility == V.PUBLIC:
        return True
    if not user or not user.is_authenticated:
        return False
    if post.visibility == V.PUBLIC_AUTH:
        return True
    if post.visibility == V.SUBSCRIBERS:
        return Subscription.objects.filter(subscriber=user, author=post.author).exists()
    if post.visibility == V.PAID:
        return Subscription.objects.filter(
            subscriber=user,
            author=post.author,
            tier=Subscription.Tier.PAID,
        ).exists()
    return False
