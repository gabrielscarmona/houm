from unittest.mock import Mock, patch
from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from django.contrib.gis.geos import Point
from .tasks import tracking
from .models import Tracking, Houmer, RealEstate


class TrackingTestCase(TestCase):

    def setUp(self):
        call_command('loaddata', 'fixtures/users.json', verbosity=0)
        call_command('loaddata', 'fixtures/houmers.json', verbosity=0)
        call_command('loaddata', 'fixtures/realestates.json', verbosity=0)
        self.houmer_user_id = Houmer.objects.get(user__username='houmer1').user.id
        self.real_estate = RealEstate.objects.get(id=1)

    def test_save_single_tracking(self):
        tracking(self.houmer_user_id, -34.5, -58.4)
        saved_tracking = Tracking.objects.first()
        self.assertEquals(saved_tracking.speed, 0)
        self.assertEquals(saved_tracking.duration, 0)
        self.assertEquals(saved_tracking.geom.wkt, Point(-34.5, -58.4).wkt)

    @patch('django.utils.timezone.now')
    def test_speed_tracking(self, mock_timezone):
        mock_timezone.return_value = datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        tracking(self.houmer_user_id, -34.5, -58.4)
        first_tracking = Tracking.objects.first()

        mock_timezone.return_value = datetime(2022, 1, 1, 0, 1, 0, tzinfo=timezone.utc)
        tracking(self.houmer_user_id, -34.5, -58.5)
        last_tracking = Tracking.objects.latest('created')

        self.assertEquals(first_tracking.speed, 0)
        self.assertEquals(first_tracking.duration, 0)
        self.assertEquals(first_tracking.geom.wkt, Point(-34.5, -58.4).wkt)

        self.assertEquals(last_tracking.speed, 551)
        self.assertEquals(last_tracking.duration, 0)
        self.assertEquals(last_tracking.geom.wkt, Point(-34.5, -58.5).wkt)

    @patch('django.utils.timezone.now')
    def test_duration_tracking(self, mock_timezone):
        mock_timezone.return_value = datetime(2022, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        tracking(self.houmer_user_id, -58.4256879365174, -34.5923050897605)
        first_tracking = Tracking.objects.first()
        mock_timezone.return_value = datetime(2022, 1, 1, 0, 10, 0, tzinfo=timezone.utc)
        tracking(self.houmer_user_id, -58.4256879365174, -34.5923050897605)
        last_tracking = Tracking.objects.latest('created')

        self.assertEquals(first_tracking.real_estate.id, 1)
        self.assertEquals(first_tracking.duration, 0)
        self.assertEquals(last_tracking.duration, 600)
