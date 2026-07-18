from django.db import migrations, models


def unpublished_to_draft(apps, schema_editor):
    Post = apps.get_model('posts', 'Post')
    Post.objects.filter(is_published=False).update(visibility='draft')


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_post_category_required'),
    ]

    operations = [
        migrations.RunPython(unpublished_to_draft, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='post',
            name='is_published',
        ),
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.CharField(
                choices=[
                    ('public', 'Все'),
                    ('public_auth', 'Авторизованные пользователи'),
                    ('subscribers', 'Только подписчики'),
                    ('paid', 'Только платные подписчики'),
                    ('draft', 'Только я (черновик)'),
                ],
                default='public',
                max_length=20,
                verbose_name='Видимость поста',
            ),
        ),
    ]
