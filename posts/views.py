from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .forms import PostForm
from .models import Post


def post_list(request):
    qs = Post.objects.select_related('author', 'category').order_by('-created_at')
    if request.user.is_authenticated:
        posts = qs.filter(
            Q(is_published=True) | Q(author=request.user),
        ).distinct()
    else:
        posts = qs.filter(is_published=True)
    return render(request, 'posts/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author', 'category'), pk=pk)
    if not post.is_published and post.author_id != getattr(request.user, 'id', None):
        messages.error(request, 'Пост недоступен к просмотру')
        return redirect('posts:list')
    return render(request, 'posts/post_detail.html', {'post': post})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост создан')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'posts/post_form.html',
                  {'form': form, 'form_title': 'Новый пост', 'cancel_url': None}, )


@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлен')
            return redirect('posts:detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/post_form.html',
                  {'form': form, 'form_title': 'Редактировать пост', 'cancel_url': post.get_absolute_url()}, )


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удален')
        return redirect('posts:list')
    return render(request, 'posts/post_confirm_delete.html', {'post': post})
