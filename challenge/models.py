from django.contrib.gis.db import models


class Houmer(models.Model):
    """Represents a user who works as a houmer."""

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class RealEstate(models.Model):
    """Represents a real estate available at Houm."""

    address = models.CharField(max_length=200)
    area = models.IntegerField()
    geom = models.PointField()

    def __str__(self):
        return self.address


class Tracking(models.Model):
    """Represents a tracking record for houmers.
        @user: tracked user
        @created: timestamp when the coordinates are received
        @real_estate: real estate reference if current position is near this one
        @duration[seconds]: time spent by the houmer at the real estate relative to previous tracking record
        @speed[km/h]: speed of the houmer relative to previous tracking record
    """

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created = models.DateTimeField()
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE, null=True)
    duration = models.IntegerField()
    speed = models.IntegerField()
    geom = models.PointField()

    def __str__(self):
        return self.geom.wkt
