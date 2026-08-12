from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import DetailView, FormView, UpdateView

from apps.subscriptions.models import Subscription
from substack_app import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import User


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Успешная регистрация')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return response


class UserLoginView(LoginView, LoginRequiredMixin):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm
    success_url = settings.LOGIN_REDIRECT_URL

    def form_invalid(self, form):
        messages.error(self.request, 'Неправильный логин или пароль')
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы вышли из аккаунта')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['me'] = self.request.user
        context['user'] = self.object
        context['is_own_profile'] = self.object == self.request.user
        context['is_subscribed'] = (
            not context['is_own_profile']
            and Subscription.objects.filter(
                subscriber=self.request.user,
                author=self.object,
            ).exists()
        )
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'users/profile_edit.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj != request.user:
            messages.error(request, 'Вы можете редактировать только свой профиль.')
            return redirect('users:profile', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        old_avatar_name = self.object.avatar.name if self.object.avatar else None
        response = super().form_valid(form)

        new_avatar_name = self.object.avatar.name if self.object.avatar else None
        if (
            old_avatar_name
            and old_avatar_name != new_avatar_name
            and 'avatar' in self.request.FILES
        ):
            self.object.avatar.storage.delete(old_avatar_name)

        messages.success(self.request, 'Профиль успешно обновлен!')
        return response

    def get_success_url(self):
        return reverse('users:profile', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['me'] = self.request.user
        context['user'] = self.object
        context['form_title'] = 'Редактировать профиль'
        return context

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{error}')
        return super().form_invalid(form)


@login_required
def chats_view(request):
    return render(request, 'users/chats.html')
