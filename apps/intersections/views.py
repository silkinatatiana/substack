from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from apps.intersections.models import LikePost, Comment, LikeComment, CommentAnswer
from apps.posts.models import Post


def _liked_comment_ids(user, post=None):
    if not user.is_authenticated:
        return set()
    qs = LikeComment.objects.filter(user=user, comment__isnull=False)
    if post is not None:
        qs = qs.filter(comment__post=post)
    return set(qs.values_list('comment_id', flat=True))


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

        LikePost.objects.get_or_create(
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
        deleted, _ = LikePost.objects.filter(
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
                ),
            ),
            pk=kwargs['pk'],
        )

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
            return redirect('posts:detail', pk=post.pk)

        Comment.objects.create(
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

        LikeComment.objects.get_or_create(
            user=request.user,
            comment=comment,
        )
        return redirect(self._next_url(request, comment.post))

    def _next_url(self, request, post):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return next_url
        return reverse('posts:detail', kwargs={'pk': post.pk})


class UnlikeCommentView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        deleted, _ = LikeComment.objects.filter(
            user=request.user,
            comment=comment,
        ).delete()

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('posts:detail', pk=comment.post_id)


class CreateCommentAnswerView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, pk: int):
        parent_comment = get_object_or_404(Comment, pk=pk)
        answer = (request.POST.get('text') or '').strip()

        if not answer:
            messages.error(request, 'Ответ на комментарий не может быть пустым')
            return redirect('posts:detail', pk=parent_comment.post_id)

        CommentAnswer.objects.create(
            user=request.user,
            parent_comment=parent_comment,
            text=answer
        )
        return redirect(self._next_url(request, parent_comment.post))

    def _next_url(self, request, post):
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return next_url
        return reverse('posts:detail', kwargs={'pk': post.pk})


class UpdateCommentAnswerView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.comment = get_object_or_404(CommentAnswer, pk=kwargs['pk'])

    def post(self, request, pk):
        if self.comment.user != request.user:
            messages.error(request, 'Редактировать можно только свои комментарии')
            return redirect('posts:detail', pk=self.comment.parent_comment.post_id)

        answer = (request.POST.get('text') or '').strip()

        if not answer:
            messages.error(request, 'Ответ на комментарий не может быть пустым')
            return redirect('posts:detail', pk=self.comment.parent_comment.post_id)

        self.comment.text = answer
        self.comment.save(update_fields=['text'])

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('posts:detail', pk=self.comment.parent_comment.post_id)


class RemoveCommentAnswerView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.answer_to_delete = get_object_or_404(CommentAnswer, pk=kwargs['pk'])

    def post(self, request, pk):
        if self.answer_to_delete.user != request.user: #TODO вынести проверку в отдельный метод
            messages.error(request, 'Удалять можно только свои комментарии')
            return redirect('posts:detail', pk=self.answer_to_delete.parent_comment.post_id)
        self.answer_to_delete.delete()

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        post_id = self.answer_to_delete.parent_comment.post_id
        return redirect('posts:detail', pk=post_id)