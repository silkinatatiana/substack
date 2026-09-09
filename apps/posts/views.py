from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max, Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from apps.intersections.models import Comment, CommentAnswer, LikePost
from apps.intersections.views import _liked_comment_ids
from apps.subscriptions.models import Subscription

from .access import post_visible_filter, user_can_view_post
from .forms import PostForm
from .models import Post, PostImage


def _comments_prefetch():
    return Prefetch(
        'comments',
        queryset=(
            Comment.objects
            .select_related('user')
            .prefetch_related(
                Prefetch(
                    'answers',
                    queryset=(
                        CommentAnswer.objects
                        .select_related('user')
                        .order_by('created_at')
                    ),
                ),
            )
            .annotate(likes_count=Count('likes', distinct=True))
            .order_by('-created_at')
        ),
    )


def _post_queryset(*, with_comments=False):
    qs = Post.objects.select_related('author', 'category').prefetch_related('images')
    if with_comments:
        qs = qs.prefetch_related(_comments_prefetch())
    return qs.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    )


def _subscribed_author_ids(user):
    if not user.is_authenticated:
        return set()
    return set(
        Subscription.objects.filter(subscriber=user).values_list('author_id', flat=True)
    )


def _liked_post_ids(user):
    if not user.is_authenticated:
        return set()
    return set(
        LikePost.objects.filter(user=user).values_list('post_id', flat=True)
    )


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return (
            _post_queryset()
            .order_by('-created_at')
            .filter(post_visible_filter(self.request.user))
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribed_author_ids'] = _subscribed_author_ids(self.request.user)
        context['liked_post_ids'] = _liked_post_ids(self.request.user)
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return _post_queryset(with_comments=True)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get('pk')
        post = get_object_or_404(queryset, pk=pk)

        if not user_can_view_post(self.request.user, post):
            messages.error(self.request, 'Пост недоступен к просмотру')
            raise Http404 # TODO изменить статус код и ошибку на ресурс не найден

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['me'] = self.request.user
        context['subscribed_author_ids'] = _subscribed_author_ids(self.request.user)
        context['liked_post_ids'] = _liked_post_ids(self.request.user)
        context['liked_comment_ids'] = _liked_comment_ids(self.request.user, self.object)
        return context

def _save_post_images(post, image_files):
    max_position = post.images.aggregate(Max('position'))['position__max']
    next_position = (max_position + 1) if max_position is not None else 0
    created_ids = []

    for image_file in image_files:
        if image_file:
            image = PostImage.objects.create(
                post=post,
                image=image_file,
                position=next_position,
            )
            created_ids.append(image.pk)
            next_position += 1

    return created_ids


def _resolve_image_order(order_raw, new_image_ids):
    image_ids = []

    for order_entry in order_raw.split(','):
        order_entry = order_entry.strip()
        if not order_entry:
            continue
        if order_entry.startswith('new:'):
            try:
                index = int(order_entry.split(':', 1)[1])
            except (IndexError, ValueError):
                continue
            if 0 <= index < len(new_image_ids):
                image_ids.append(new_image_ids[index])
        else:
            try:
                image_ids.append(int(order_entry))
            except ValueError:
                continue

    return image_ids


def _parse_id_list(raw):
    if not raw:
        return []

    try:
        return [int(x) for x in raw.split(',') if x.strip()]
    except ValueError:
        return []


def _delete_post_images(post, deleted_raw):
    image_ids = _parse_id_list(deleted_raw)
    if image_ids:
        post.images.filter(pk__in=image_ids).delete()

def _apply_image_order(post, order_raw, new_image_ids=None):
    if new_image_ids is None:
        new_image_ids = []

    image_ids = _resolve_image_order(order_raw, new_image_ids) if order_raw else []
    if not image_ids:
        return

    images = {img.pk: img for img in post.images.filter(pk__in=image_ids)}

    for position, image_id in enumerate(image_ids):
        image = images.get(image_id)
        if image:
            image.position = position
            image.save(update_fields=['position'])


class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    template_name = 'posts/post_form.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        _save_post_images(post, form.cleaned_data.get('images', []))
        messages.success(self.request, 'Пост создан')
        return redirect('posts:detail', pk=post.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Новый пост'
        context['cancel_url'] = None
        return context


class PostUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    template_name = 'posts/post_form.html'
    form_class = PostForm

    def form_valid(self, form):
        response = super().form_valid(form)
        _delete_post_images(self.object, form.cleaned_data.get('deleted_image_ids', ''))
        new_image_ids = _save_post_images(self.object, form.cleaned_data.get('images', []))
        _apply_image_order(self.object, form.cleaned_data.get('image_order', ''), new_image_ids)
        messages.success(self.request, 'Пост обновлен')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать пост'
        context['cancel_url'] = self.object.get_absolute_url()
        return context


class PostDeleteView(DeleteView, LoginRequiredMixin):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('posts:list')

    def form_valid(self, form):
        messages.success(self.request, 'Пост удален')
        return super().form_valid(form)
