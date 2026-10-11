from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.intersections.models import Comment
from apps.posts.models import Post


class CommentService:

    @staticmethod
    def create_comment(user, post_id: int, text: str, parent_id: int = None) -> dict:
        """Создает комментарий с валидацией."""
        cleaned_text = (text or '').strip()
        if not cleaned_text:
            return {'success': False, 'error': 'Комментарий не может быть пустым'}

        post = get_object_or_404(Post, pk=post_id)

        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(
                Comment,
                pk=parent_id,
                post=post,
            )

        new_comment = Comment.objects.create(
            user=user,
            post=post,
            text=cleaned_text,
            parent_comment=parent_comment,
        )

        return {'success': True, 'comment': new_comment}

    @staticmethod
    def update_comment_text(comment, new_text: str) -> dict:
        """Обновляет текст комментария после валидации."""
        cleaned_text = (new_text or '').strip()
        if not cleaned_text:
            return {
                'success': False,
                'error': 'Комментарий не может быть пустым'
            }
        if len(cleaned_text) > 5000:
            return {'success': False, 'error': 'Слишком длинный комментарий'}
        if comment.created_at < timezone.now() - timedelta(hours=24):
            return {'success': False, 'error': 'Редактирование недоступно'}

        comment.text = cleaned_text
        comment.save(update_fields=['text'])

        return {'success': True, 'new_text': comment.text}