import time

from api.filters import RaidFilter
from api.models import Raid
from api.serializers import RaidSerializer
from api.tasks import send_raid_notification_email
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView


class RaidViewSet(viewsets.ModelViewSet):
    queryset = (
        Raid.objects.select_related("dungeon")
        .prefetch_related(
            "participations", "participations__hunter", "participations__hunter__skills"
        )
        .all()
    )
    serializer_class = RaidSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = RaidFilter
    search_fields = ["name"]
    ordering_fields = ["date", "name"]

    @method_decorator(cache_page(60 * 15, key_prefix="raid_list"))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        raid = serializer.save()
        send_raid_notification_email.delay(raid.id)

    def get_queryset(self):
        time.sleep(2)
        qs = super().get_queryset()
        return qs

    def get_permissions(self):
        self.permission_classes = [permissions.IsAuthenticated]
        if self.request.method in ("POST", "PUT", "DELETE"):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
