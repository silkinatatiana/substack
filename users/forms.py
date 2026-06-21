from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from PIL import Image
import io

User = get_user_model()

ALLOWED_AVATAR_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_AVATAR_FORMATS = {'JPEG', 'PNG'}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


class AvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
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


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    bio = forms.CharField(required=False,
                          widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell about yourself',
                                                       'rows': 4}))

    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('User with this email already exists')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.bio = self.cleaned_data.get('bio', '')
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username