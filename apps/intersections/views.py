from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from apps.intersections.models import Like, Comment
from apps.posts.models import Post


class LikeListView(LoginRequiredMixin, ListView):
    model = Like
    template_name = 'intersections/like_list.html'
    context_object_name = 'like_list'
    paginate_by = 20

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.post = get_object_or_404(Post, pk=kwargs['pk'])

    def get_queryset(self):
        qs = (
            Like.objects
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

        Like.objects.get_or_create(
            user=request.user,
            post=post,
        )
        return redirect(self._next_url(request, post))

    def _next_url(self, request, post):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return next_url
        return reverse('posts:detail', kwargs={'pk': post.pk})


class UnlikeView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        deleted, _ = Like.objects.filter(
            user=request.user,
            post=post,
        ).delete()

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('posts:detail', pk=pk)


class CommentListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'intersections/comment_list.html'
    context_object_name = 'comment_list'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post
        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.post = get_object_or_404(Post, pk=kwargs['pk'])

    def get_queryset(self):
        qs = (
            Comment.objects
            .filter(post=self.post)
            .select_related('user')
            .order_by('-created_at')
        )

        return qs


class CreateCommentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk: int):
        post = get_object_or_404(Post, pk=pk)
        text = (request.POST.get('text') or '').strip()

        if not text:
            messages.error(request, 'Комментарий не может быть пустым')
            return redirect('posts:detail', pk=self.comment.post_id)

        Comment.objects.get_or_create(
            user=request.user,
            post=post,
            text=text
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


class RefactorCommentView(LoginRequiredMixin, View):
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
        return redirect('posts:detail', pk=pk)