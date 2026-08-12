from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .models import Subscription

User = get_user_model()


class SubscriberListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscriptions/subscriber_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 20

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.author = get_object_or_404(User, pk=kwargs['pk'])

    def get_queryset(self):
        qs = (
            Subscription.objects
            .filter(author=self.author)
            .select_related('subscriber')
            .order_by('-created_at')
        )
        tier = self.request.GET.get('tier')
        if tier in {Subscription.Tier.FREE, Subscription.Tier.PAID}:
            qs = qs.filter(tier=tier)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author

        context['is_own_author'] = self.request.user.pk == self.author.pk  # todo вынести в отельную общую функцию
        context['active_tier'] = self.request.GET.get('tier', '')
        context['title'] = 'Подписчики'
        return context


class SubscribeView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)

        if author.pk == request.user.pk:
            messages.error(request, 'Нельзя подписаться на себя')
            return redirect('users:profile', pk=pk)

        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            author=author,
            defaults={'tier': Subscription.Tier.FREE},
        )

        if created:
            messages.success(request, f'Вы подписались на {author.username}')
        else:
            messages.info(request, 'Вы уже подписаны')

        return redirect(self._next_url(request, author))

    def _next_url(self, request, author):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return next_url
        return reverse('users:profile', kwargs={'pk': author.pk})


class UnsubscribeView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        deleted, _ = Subscription.objects.filter(
            subscriber=request.user,
            author=author,
        ).delete()

        if deleted:
            messages.success(request, f'Вы отписались от {author.username}')
        else:
            messages.info(request, 'Вы не были подписаны')

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('users:profile', pk=pk)


class SubscribtionsListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscriptions/subscriber_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 20

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.author = get_object_or_404(User, pk=kwargs['pk'])

    def get_queryset(self):
        qs = (
            Subscription.objects
            .filter(subscriber=self.author)
            .select_related('author')
            .order_by('-created_at')
        )

        print(qs)
        tier = self.request.GET.get('tier')
        if tier in {Subscription.Tier.FREE, Subscription.Tier.PAID}:
            qs = qs.filter(tier=tier)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author

        context['is_own_author'] = self.request.user.pk == self.author.pk  # todo вынести в отельную общую функцию
        context['active_tier'] = self.request.GET.get('tier', '')
        context['title'] = 'Подписки'
        return context
