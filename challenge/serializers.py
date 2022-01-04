from rest_framework import serializers
from .models import Tracking, Houmer


class HoumerSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Houmer
        fields = ('id', 'name',)


class AttendanceSerializer(serializers.Serializer):
    total_duration = serializers.IntegerField()
    geom = serializers.CharField(max_length=200)


class SpeedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tracking
        fields = ('id', 'created', 'speed')


class TrackingSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=True)
    lng = serializers.FloatField(required=True)
