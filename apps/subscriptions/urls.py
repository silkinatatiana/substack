from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path(
        'author/<int:pk>/my/',
        views.SubscriberListView.as_view(),
        name='list_subscribes',
    ),
    path(
        'author/<int:pk>/subscribe/',
        views.SubscribeView.as_view(),
        name='subscribe',
    ),
    path(
        'author/<int:pk>/unsubscribe/',
        views.UnsubscribeView.as_view(),
        name='unsubscribe',
    ),
    path(
            'author/<int:pk>/for/',
            views.SubscribtionsListView.as_view(),
            name='list_subscriptions',
        ),
]
