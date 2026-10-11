from django.core.exceptions import PermissionDenied


def ensure_user_is_owner(instance_user, current_user):
    if instance_user != current_user:
        raise PermissionDenied("У вас нет прав на редактирование этого комментария.")