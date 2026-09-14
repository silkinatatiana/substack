import django.db.models.deletion
from django.db import migrations, models


def forwards_unify_comments(apps, schema_editor):
    Comment = apps.get_model('intersections', 'Comment')
    CommentAnswer = apps.get_model('intersections', 'CommentAnswer')
    LikeComment = apps.get_model('intersections', 'LikeComment')

    answer_id_to_comment_id = {}
    for answer in CommentAnswer.objects.all().order_by('id'):
        comment = Comment.objects.create(
            post_id=answer.parent_comment.post_id,
            parent_comment_id=answer.parent_comment_id,
            user_id=answer.user_id,
            text=answer.text,
            created_at=answer.created_at,
            updated_at=answer.updated_at,
        )
        answer_id_to_comment_id[answer.id] = comment.id

    for like in LikeComment.objects.filter(comment_answer_id__isnull=False):
        new_comment_id = answer_id_to_comment_id.get(like.comment_answer_id)
        if new_comment_id is None:
            like.delete()
            continue
        like.comment_id = new_comment_id
        like.comment_answer_id = None
        like.save(update_fields=['comment_id', 'comment_answer_id'])


def backwards_split_comments(apps, schema_editor):
    Comment = apps.get_model('intersections', 'Comment')
    CommentAnswer = apps.get_model('intersections', 'CommentAnswer')
    LikeComment = apps.get_model('intersections', 'LikeComment')

    comment_id_to_answer_id = {}
    for comment in Comment.objects.filter(parent_comment_id__isnull=False).order_by('id'):
        answer = CommentAnswer.objects.create(
            parent_comment_id=comment.parent_comment_id,
            user_id=comment.user_id,
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
        comment_id_to_answer_id[comment.id] = answer.id

    for like in LikeComment.objects.filter(comment_id__in=comment_id_to_answer_id):
        like.comment_answer_id = comment_id_to_answer_id[like.comment_id]
        like.comment_id = None
        like.save(update_fields=['comment_id', 'comment_answer_id'])

    Comment.objects.filter(parent_comment_id__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('intersections', '0003_alter_comment_post_alter_comment_user_commentanswer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='parent_comment',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='answers',
                to='intersections.comment',
                verbose_name='Родительский комментарий',
            ),
        ),
        migrations.AlterField(
            model_name='commentanswer',
            name='parent_comment',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='legacy_answers',
                to='intersections.comment',
                verbose_name='Комментарий',
            ),
        ),
        migrations.RunPython(forwards_unify_comments, backwards_split_comments),
        migrations.RemoveConstraint(
            model_name='likecomment',
            name='like_comment_exactly_one_target',
        ),
        migrations.RemoveConstraint(
            model_name='likecomment',
            name='unique_comment_like',
        ),
        migrations.RemoveConstraint(
            model_name='likecomment',
            name='unique_comment_answer_like',
        ),
        migrations.RemoveField(
            model_name='likecomment',
            name='comment_answer',
        ),
        migrations.DeleteModel(
            name='CommentAnswer',
        ),
        migrations.AlterField(
            model_name='likecomment',
            name='comment',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='likes',
                to='intersections.comment',
                verbose_name='Комментарий',
            ),
        ),
        migrations.AddConstraint(
            model_name='likecomment',
            constraint=models.UniqueConstraint(
                fields=('user', 'comment'),
                name='unique_comment_like',
            ),
        ),
    ]
