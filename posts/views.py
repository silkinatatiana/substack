from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.generic import DetailView

from .access import post_visible_filter, user_can_view_post
from .forms import PostForm
from .models import Post, PostImage


def _post_queryset():
    return Post.objects.select_related('author', 'category').prefetch_related('images').annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    )


def post_list(request):
    qs = _post_queryset().order_by('-created_at')
    posts = qs.filter(post_visible_filter(request.user)).distinct()
    return render(request, 'posts/post_list.html', {'posts': posts, 'me': request.user})


class PostDetail(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return _post_queryset()

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get('pk')
        post = get_object_or_404(queryset, pk=pk)

        if not user_can_view_post(self.request.user, post):
            messages.error(self.request, 'Пост недоступен к просмотру')
            raise Http404

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['me'] = self.request.user
        return context


def _save_post_images(post, image_files):
    max_position = post.images.aggregate(Max('position'))['position__max']
    next_position = (max_position + 1) if max_position is not None else 0

    for image_file in image_files:
        if image_file:
            PostImage.objects.create(post=post, image=image_file, position=next_position)
            next_position += 1


def _apply_image_order(post, order_raw):
    if not order_raw:
        return

    try:
        image_ids = [int(x) for x in order_raw.split(',') if x.strip()]
    except ValueError:
        return

    images = {img.pk: img for img in post.images.filter(pk__in=image_ids)}

    for position, image_id in enumerate(image_ids):
        image = images.get(image_id)
        if image:
            image.position = position
            image.save(update_fields=['position'])

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            _save_post_images(post, form.cleaned_data.get('images', []))
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
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            _save_post_images(post, form.cleaned_data.get('images', []))
            _apply_image_order(post, form.cleaned_data.get('image_order', ''))
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
