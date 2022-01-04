from celery import shared_task
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D, Distance
from django.utils import timezone
from geopy.distance import distance
from .models import Tracking, RealEstate


def latest_tracking(user_id):
    """Returns latest tracking for a given user or None otherwise."""
    try:
        return Tracking.objects.filter(user_id=user_id).latest('created')
    except Tracking.DoesNotExist:
        return None


def nearest_real_estate(current_position, distance_meters=50):
    """Returns a nearest Real Estate within a given distance measured in meters or None otherwise."""

    return RealEstate.objects.filter(geom__distance_lte=(current_position, D(m=distance_meters))).first()


def calculate_speed(current_position, current_time, latest_tracking) -> int:
    """Returns the relative speed betwen two given points represented as km/hs."""
    if not latest_tracking:
        return 0
    diff_distance = distance(current_position, latest_tracking.geom).kilometers
    diff_time = (current_time - latest_tracking.created).total_seconds() / 60 / 60
    return round(diff_distance / diff_time)


def calculate_duration(current_time, nearest_real_estate, latest_tracking) -> int:
    """Returns the duration in seconds spent near the latest real estate."""

    if latest_tracking and nearest_real_estate and nearest_real_estate == latest_tracking.real_estate:
        return (current_time - latest_tracking.created).total_seconds()
    return 0


@shared_task
def tracking(user_id: int, lng: float, lat: float):
    """Calculates the speed and the duration relative to the latest tracking and saves a new tracking record."""

    current_position = Point(lng, lat)
    latest = latest_tracking(user_id)
    nearest = nearest_real_estate(current_position)
    now = timezone.now()
    duration = calculate_duration(now, nearest, latest)
    speed = calculate_speed(current_position, now, latest)

    Tracking.objects.create(
        created=now, user_id=user_id, geom=current_position, real_estate=nearest, duration=duration, speed=speed
    )
