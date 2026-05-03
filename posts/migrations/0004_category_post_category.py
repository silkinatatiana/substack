# Категории постов (модель Category + Post.category)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_post_author_alter_post_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(max_length=96, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='posts',
                to='posts.category',
                verbose_name='Категория',
            ),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['category', 'created_at'], name='posts_post_cat_created_idx'),
        ),
    ]
