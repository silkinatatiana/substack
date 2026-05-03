from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'is_published', 'visibility']
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
            'is_published': forms.CheckboxInput(),
        }
