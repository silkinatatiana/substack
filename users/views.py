from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from substack_app import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AvatarForm
from .models import User


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect(settings.LOGIN_URL)


@login_required
def profile_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'users/profile.html', {'user': user, 'me':request.user})


@login_required
def chats_view(request):
    return render(request, 'users/chats.html')


@login_required
def change_avatar_view(request):
    user = User.objects.get(pk=request.user.pk)

    if request.method == 'POST':
        old_avatar_name = user.avatar.name if user.avatar else None
        form = AvatarForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if 'avatar' not in request.FILES:
                messages.warning(request, 'Выберите файл для загрузки')
            else:
                user = form.save()
                if old_avatar_name and old_avatar_name != user.avatar.name:
                    user.avatar.storage.delete(old_avatar_name)
                messages.success(request, 'Аватар успешно обновлен!')
                return redirect('users:profile', pk=user.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = AvatarForm(instance=user)

    return render(request, 'users/change_avatar.html', {'form': form})