from datetime import timedelta

from django.utils import timezone


def get_activity_status(last_activity_date, now=None):
    """Return the profile activity state and a human-readable tooltip."""
    now = now or timezone.now()

    if last_activity_date is None:
        return {
            'is_active': False,
            'label': 'Давно не был(а) активен(на)',
        }

    elapsed = max(now - last_activity_date, timedelta(0))

    is_active = elapsed < timedelta(minutes=5)
    if is_active:
        label = 'Активен'
    elif elapsed < timedelta(minutes=15):
        label = 'Был(а) активен(на) меньше 15 минут назад'
    elif elapsed < timedelta(minutes=30):
        label = 'Был(а) активен(на) меньше 30 минут назад'
    elif elapsed < timedelta(hours=1):
        label = 'Был(а) активен(на) меньше часа назад'
    elif elapsed < timedelta(days=1):
        label = 'Был(а) активен(на) меньше дня назад'
    elif elapsed < timedelta(days=7):
        label = 'Был(а) активен(на) меньше недели назад'
    else:
        label = 'Давно не был(а) активен(на)'

    return {
        'is_active': is_active,
        'label': label,
    }
