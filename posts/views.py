from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.generic import DetailView

from .access import post_visible_filter, user_can_view_post
from .forms import PostForm
from .models import Post


def post_list(request):
    qs = Post.objects.select_related('author', 'category').order_by('-created_at')
    posts = qs.filter(post_visible_filter(request.user)).distinct()
    return render(request, 'posts/post_list.html', {'posts': posts})


class PostDetail(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.select_related('author', 'category')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get('pk')
        post = get_object_or_404(queryset, pk=pk)

        if not user_can_view_post(self.request.user, post):
            messages.error(self.request, 'Пост недоступен к просмотру')
            raise Http404

        return post


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
