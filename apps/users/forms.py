from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from PIL import Image
import io
import re

User = get_user_model()

ALLOWED_AVATAR_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_AVATAR_FORMATS = {'JPEG', 'PNG'}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


def _clean_avatar_file(avatar):
    if not avatar or not isinstance(avatar, UploadedFile):
        return avatar

    if avatar.size > MAX_AVATAR_SIZE:
        raise forms.ValidationError('Размер файла не должен превышать 5MB')

    avatar.seek(0)
    content = avatar.read()

    ext = avatar.name.rsplit('.', 1)[-1].lower() if '.' in avatar.name else ''
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise forms.ValidationError(
            f'Допустимые форматы: {", ".join(sorted(ALLOWED_AVATAR_EXTENSIONS))}'
        )

    try:
        with Image.open(io.BytesIO(content)) as img:
            img.verify()
        with Image.open(io.BytesIO(content)) as img:
            if img.format not in ALLOWED_AVATAR_FORMATS:
                raise forms.ValidationError('Допустимые форматы: jpg, jpeg, png')
    except forms.ValidationError:
        raise
    except Exception:
        raise forms.ValidationError('Файл не является допустимым изображением')

    return SimpleUploadedFile(
        avatar.name,
        content,
        content_type=getattr(avatar, 'content_type', 'application/octet-stream'),
    )


class AvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']

    def clean_avatar(self):
        return _clean_avatar_file(self.cleaned_data.get('avatar'))


class ProfileUpdateForm(forms.ModelForm):
    tg_name = forms.CharField(
        required=False,
        max_length=21,
        label='Телеграм',
        help_text='Только ник без ссылки, например: username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'username (без @)',
        }),
    )

    class Meta:
        model = User
        fields = [
            'username',
            'bio',
            'avatar',
            'website_url',
            'tg_name',
            'monetizations',
            'price_month',
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Расскажите о себе',
                'rows': 4,
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com',
            }),
            'monetizations': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
            'price_month': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '99.9',
            }),
        }

    def clean_avatar(self):
        return _clean_avatar_file(self.cleaned_data.get('avatar'))

    def clean_tg_name(self):
        tg_name = (self.cleaned_data.get('tg_name') or '').strip()
        if not tg_name:
            return ''

        tg_name = tg_name.lstrip('@')

        if not tg_name:
            return ''

        if not re.fullmatch(r'[A-Za-z0-9_]{5,20}', tg_name):
            raise forms.ValidationError(
                'Укажите только ник Telegram (5–20 символов: латиница, цифры, _)'
            )

        return tg_name


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    )
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}),
    )
    bio = forms.CharField(
        required=False,
        label='О себе',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Расскажите о себе',
            'rows': 4,
        }),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.bio = self.cleaned_data.get('bio', '')
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username
