import io

from PIL import Image
from django import forms
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile

from .models import Post

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def validate_image_upload(image):
    if not image or not isinstance(image, UploadedFile):
        return image

    if image.size > MAX_IMAGE_SIZE:
        raise forms.ValidationError('Размер файла не должен превышать 5MB')

    image.seek(0)
    content = image.read()

    ext = image.name.rsplit('.', 1)[-1].lower() if '.' in image.name else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise forms.ValidationError(
            f'Допустимые форматы: {", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))}'
        )

    try:
        with Image.open(io.BytesIO(content)) as img:
            img.verify()
        with Image.open(io.BytesIO(content)) as img:
            if img.format not in ALLOWED_IMAGE_FORMATS:
                raise forms.ValidationError('Допустимые форматы: jpg, jpeg, png')
    except forms.ValidationError:
        raise
    except Exception:
        raise forms.ValidationError('Файл не является допустимым изображением')

    return SimpleUploadedFile(
        image.name,
        content,
        content_type=getattr(image, 'content_type', 'application/octet-stream'),
    )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'category', 'visibility']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Заголовок'}
            ),
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Текст поста',
                    'rows': 12,
                }
            ),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(
                attrs={
                    'accept': 'image/jpeg,image/png,.jpg,.jpeg,.png',
                    'class': 'file-upload-input',
                }
            ),
        }

    def clean_image(self):
        return validate_image_upload(self.cleaned_data.get('image'))


class ImageForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image']
        widgets = {
            'image': forms.FileInput(
                attrs={
                    'accept': 'image/jpeg,image/png,.jpg,.jpeg,.png',
                    'class': 'file-upload-input',
                }
            ),
        }

    def clean_image(self):
        return validate_image_upload(self.cleaned_data.get('image'))
