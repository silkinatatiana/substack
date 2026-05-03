
import django.db.models.deletion
from django.db import migrations, models


def assign_default_category(apps, schema_editor):
    Post = apps.get_model('posts', 'Post')
    Category = apps.get_model('posts', 'Category')
    orphans = Post.objects.filter(category__isnull=True)
    if not orphans.exists():
        return
    cat, _ = Category.objects.get_or_create(
        name='Общее',
        defaults={'slug': 'obshchee'},
    )
    orphans.update(category=cat)


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_category_post_category'),
    ]

    operations = [
        migrations.RunPython(assign_default_category, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='posts',
                to='posts.category',
                verbose_name='Категория',
            ),
        ),
    ]
