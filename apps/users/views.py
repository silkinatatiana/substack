from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import FormView, UpdateView

from substack_app import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AvatarForm
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


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AvatarForm
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['me'] = self.request.user
        context['user'] = self.object

        if self.object == self.request.user:
            context['form'] = self.get_form()

        return context

    def form_valid(self, form):
        if self.object != self.request.user:
            messages.error(self.request, 'Вы можете менять аватар только в своем профиле.')
            return redirect(settings.LOGIN_REDIRECT_URL)

        if 'avatar' not in self.request.FILES:
            messages.warning(self.request, 'Выберите файл для загрузки')
            return self.form_invalid(form)

        old_avatar_name = self.object.avatar.name if self.object.avatar else None
        self.object = form.save()

        new_avatar_name = self.object.avatar.name if self.object.avatar else None
        if old_avatar_name and old_avatar_name != new_avatar_name:
            self.object.avatar.storage.delete(old_avatar_name)

        messages.success(self.request, 'Аватар успешно обновлен!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('users:profile', kwargs={'pk': self.object.pk})

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{error}')
        return super().form_invalid(form)


@login_required
def chats_view(request):
    return render(request, 'users/chats.html')