from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from apps.intersections.models import Like
from apps.posts.models import Post


class LikeListView(LoginRequiredMixin, ListView):
    model = Like
    template_name = 'intersections/intersections_list.html'
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