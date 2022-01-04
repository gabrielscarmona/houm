from datetime import datetime
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db.models import Sum, F, Value, OuterRef, Subquery
from .models import Tracking, RealEstate, Houmer
from .serializers import HoumerSerializer, AttendanceSerializer, SpeedSerializer, TrackingSerializer
from .tasks import tracking


class TrackingView(viewsets.ViewSet):
    def create(self, request):
        if TrackingSerializer(data=request.data).is_valid():
            tracking.delay(request.user.id, request.data['lng'], request.data['lat'])
            return Response()
        return Response(status=status.HTTP_400_BAD_REQUEST)


class HoumerView(viewsets.ModelViewSet):
    http_method_names = ['get']
    serializer_class = HoumerSerializer
    queryset = Houmer.objects.all()

    def parse_date(self, date: str):
        try:
            return datetime.strptime(date, '%d-%m-%Y').date()
        except Exception:
            return None

    def parse_speed(self, speed: str):
        try:
            return int(speed)
        except Exception:
            return None

    @action(detail=True)
    def attendance(self, request, pk=None):
        """Given a 'date' in the format of 'dd-mm-yyyy' as a parameter returns a list of 'geom' as 'wkt' where a
        real estate exists and the 'total_duration' as minutes spent by the 'houmer' in that one.
        """

        date = self.parse_date(self.request.query_params.get('date'))
        if not date:
            return Response([])

        houmer = self.get_object()
        real_estate = RealEstate.objects.filter(id=OuterRef('real_estate_id')).values('geom')[:1]
        trackings = Tracking.objects.values(
            'user', 'real_estate'
        ).filter(
            created__date=date,
            user=houmer.user,
            real_estate__isnull=False
        ).annotate(
            geom=Subquery(real_estate)
        ).annotate(
            total_duration=Sum(F('duration') / Value(60))
        )

        serializer = AttendanceSerializer(trackings, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def speed(self, request, pk=None):
        """Given a 'date' in the format of 'dd-mm-yyyy' and a 'min_speed' as a parameter returns a list of timestamp
        'created' with the speed of that moment.
        """

        date = self.parse_date(self.request.query_params.get('date'))
        min_speed = self.parse_speed(self.request.query_params.get('min_speed'))
        if not date or not min_speed:
            return Response([])

        houmer = self.get_object()
        trackings = Tracking.objects.filter(
            created__date=date, user=houmer.user, speed__gt=min_speed
        ).order_by('-id')

        page = self.paginate_queryset(trackings)
        if page is not None:
            serializer = SpeedSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(SpeedSerializer, many=True)
        return Response(serializer.data)

