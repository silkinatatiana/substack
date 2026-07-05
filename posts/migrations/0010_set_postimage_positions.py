from django.db import migrations


def set_positions(apps, schema_editor):
    Post = apps.get_model('posts', 'Post')

    for post in Post.objects.all():
        for index, image in enumerate(post.images.order_by('created_at')):
            image.position = index
            image.save(update_fields=['position'])


def reverse_positions(apps, schema_editor):
    PostImage = apps.get_model('posts', 'PostImage')
    PostImage.objects.update(position=0)


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_alter_postimage_options_postimage_position'),
    ]

    operations = [
        migrations.RunPython(set_positions, reverse_positions),
    ]