from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_remove_is_published_expand_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='images/',
                verbose_name='Изображение',
            ),
        ),
    ]
