from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_alter_subscription_options_alter_subscription_author_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE subscriptions_subscription DROP COLUMN started_at;',
                    reverse_sql=(
                        'ALTER TABLE subscriptions_subscription '
                        'ADD COLUMN started_at datetime NOT NULL '
                        "DEFAULT CURRENT_TIMESTAMP;"
                    ),
                ),
            ],
        ),
    ]
