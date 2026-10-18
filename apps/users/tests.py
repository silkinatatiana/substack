from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone

from .activity import get_activity_status


class ActivityStatusTests(SimpleTestCase):
    def test_status_at_time_boundaries(self):
        now = timezone.now()
        cases = (
            (timedelta(minutes=4, seconds=59), True, 'меньше 5 минут'),
            (timedelta(minutes=5), False, 'меньше часа'),
            (timedelta(hours=1), False, 'меньше дня'),
            (timedelta(days=1), False, 'меньше недели'),
            (timedelta(days=7), False, 'Давно'),
        )

        for elapsed, expected_active, expected_label in cases:
            with self.subTest(elapsed=elapsed):
                status = get_activity_status(now - elapsed, now=now)
                self.assertIs(status['is_active'], expected_active)
                self.assertIn(expected_label, status['label'])

    def test_missing_activity_is_inactive(self):
        status = get_activity_status(None)

        self.assertIs(status['is_active'], False)
        self.assertIn('Давно', status['label'])
