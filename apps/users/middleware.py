from datetime import timedelta

from django.utils import timezone

from apps.users.models import User


class LastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            user = request.user
            now = timezone.now()

            last_activity = user.last_activity_date

            if (
                last_activity is None
                or now - last_activity > timedelta(minutes=5)
            ):
                User.objects.filter(pk=user.pk).update(
                    last_activity_date=now
                )

                user.last_activity_date = now

        response = self.get_response(request)

        return response