import time

from api.filters import RaidParticipationFilter
from api.models import RaidParticipation
from api.serializers import RaidParticipationSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class RaidParticipationViewSet(viewsets.ModelViewSet):
    queryset = RaidParticipation.objects.select_related("raid", "hunter").all()
    serializer_class = RaidParticipationSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RaidParticipationFilter

    @method_decorator(cache_page(60 * 15, key_prefix="participation_list"))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        time.sleep(2)

        qs = super().get_queryset()

        if not self.request.user.is_staff:
            qs = qs.filter(hunter=self.request.user)

        return qs

    def get_permissions(self):
        self.permission_classes = [permissions.IsAuthenticated]
        if self.request.method in ("POST", "PUT", "DELETE"):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def perform_create(self, serializer):
        participation = serializer.save()
