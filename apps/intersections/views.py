from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import ListView

from apps.intersections.models import LikePost, Comment, LikeComment
from apps.posts.models import Post


def _liked_comment_ids(user, post=None):
    if not user.is_authenticated:
        return set()
    qs = LikeComment.objects.filter(user=user)
    if post is not None:
        qs = qs.filter(comment__post=post)
    return set(qs.values_list('comment_id', flat=True))


def nested_answers_queryset(depth=8):
    qs = (
        Comment.objects
        .select_related('user')
        .annotate(likes_count=Count('likes', distinct=True))
        .order_by('created_at')
    )
    if depth > 0:
        qs = qs.prefetch_related(
            Prefetch('answers', queryset=nested_answers_queryset(depth - 1)),
        )
    return qs


class LikeListView(LoginRequiredMixin, ListView):
    model = LikePost
    template_name = 'intersections/like_list.html'
    context_object_name = 'like_list'
    paginate_by = 20

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.post = get_object_or_404(Post, pk=kwargs['pk'])

    def get_queryset(self):
        qs = (
            LikePost.objects
            .filter(post=self.post)
            .select_related('user')
            .order_by('-created_at')
        )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post
        return context


class LikeView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        like_exists = LikePost.objects.filter(user=request.user, post=post).exists()
        if like_exists:
            LikePost.objects.filter(
                user=request.user,
                post=post,
            ).delete()
        else:
            LikePost.objects.get_or_create(
                user=request.user,
                post=post,
            )
        is_liked = not like_exists
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'is_liked': is_liked,
                'likes_count': post.likes.count(),
            })
        return redirect(self._next_url(request, post))

    def _next_url(self, request, post):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
        ):
            return next_url
        return reverse('posts:detail', kwargs={'pk': post.pk})


class CommentListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'intersections/comment_list.html'
    context_object_name = 'comment_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post
        context['liked_comment_ids'] = _liked_comment_ids(self.request.user, self.post)
        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.post = get_object_or_404(
            Post.objects.prefetch_related(
                Prefetch(
                    'comments',
                    queryset=(
                        Comment.objects
                        .filter(parent_comment__isnull=True)
                        .select_related('user')
                        .prefetch_related(
                            Prefetch('answers', queryset=nested_answers_queryset()),
                        )
                        .annotate(likes_count=Count('likes', distinct=True))
                        .order_by('-created_at')
                    ),
                ),
            ),
            pk=kwargs['pk'],
        )

    def get_queryset(self):
        return (
            Comment.objects
            .filter(post=self.post, parent_comment__isnull=True)
            .select_related('user')
            .order_by('-created_at')
        )


class CreateCommentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk: int):
        post = get_object_or_404(Post, pk=pk)
        text = (request.POST.get('text') or '').strip()

        if not text:
            messages.error(request, 'Комментарий не может быть пустым')
            return redirect('posts:detail', pk=post.pk)

        parent_comment = None
        parent_id = (request.POST.get('parent_id') or '').strip()
        if parent_id:
            parent_comment = get_object_or_404(
                Comment,
                pk=parent_id,
                post=post,
            )

        Comment.objects.create(
            user=request.user,
            post=post,
            text=text,
            parent_comment=parent_comment,
        )
        return redirect(self._next_url(request, post))

    def _next_url(self, request, post):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return next_url
        return reverse('posts:detail', kwargs={'pk': post.pk})


class RemoveCommentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.comment = get_object_or_404(Comment, pk=kwargs['pk'])

    def post(self, request, pk):
        if self.comment.user != request.user:
            messages.error(request, 'Удалять можно только свои комментарии')
            return redirect('posts:detail', pk=self.comment.post_id)
        self.comment.delete()

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('posts:detail', pk=self.comment.post_id)


class UpdateCommentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.comment = get_object_or_404(Comment, pk=kwargs['pk'])

    def post(self, request, pk):
        if self.comment.user != request.user:
            messages.error(request, 'Редактировать можно только свои комментарии')
            return redirect('posts:detail', pk=self.comment.post_id)

        text = (request.POST.get('text') or '').strip()

        if not text:
            messages.error(request, 'Комментарий не может быть пустым')
            return redirect('posts:detail', pk=self.comment.post_id)

        self.comment.text = text
        self.comment.save(update_fields=['text'])

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('posts:detail', pk=self.comment.post_id)


class LikeCommentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        like_exists = LikeComment.objects.filter(
            user=request.user,
            comment=comment,
        ).exists()
        if like_exists:
            LikeComment.objects.filter(
                user=request.user,
                comment=comment,
            ).delete()
        else:
            LikeComment.objects.get_or_create(
                user=request.user,
                comment=comment,
            )
        is_liked = not like_exists
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'is_liked': is_liked,
                'likes_count': comment.likes.count(),
            })
        return redirect(self._next_url(request, comment.post))

    def _next_url(self, request, post):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
        ):
            return next_url
        return reverse('posts:detail', kwargs={'pk': post.pk})
