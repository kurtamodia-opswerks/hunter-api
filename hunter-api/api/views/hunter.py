import time

from api.filters import HunterFilter
from api.models import Hunter
from api.serializers import HunterSerializer
from api.tasks import send_hunter_welcome_email
from django.db.models import Case, F, IntegerField, Sum, Value, When
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class HunterViewSet(viewsets.ModelViewSet):
    queryset = (
        Hunter.objects.select_related("guild")
        .prefetch_related(
            "skills", "completed_raids", "participations", "participations__raid"
        )
        .all()
    )
    serializer_class = HunterSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = HunterFilter
    search_fields = ["username", "first_name", "last_name"]
    ordering_fields = ["date_joined", "rank"]

    @method_decorator(cache_page(60 * 15, key_prefix="hunter_list"))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        hunter = serializer.save()
        send_hunter_welcome_email.delay(hunter.id)

    def get_queryset(self):
        time.sleep(2)
        base_power = {
            "E": 10,
            "D": 30,
            "C": 50,
            "B": 80,
            "A": 120,
            "S": 200,
        }
        qs = (
            super()
            .get_queryset()
            .annotate(
                skill_power=Coalesce(Sum("skills__power"), Value(0)),
                base_power=Case(
                    *(When(rank=k, then=Value(v)) for k, v in base_power.items()),
                    output_field=IntegerField(),
                ),
                total_power=F("base_power") + F("skill_power"),
            )
            .order_by("-total_power", "id")
        )
        return qs

    def get_permissions(self):
        self.permission_classes = [permissions.AllowAny]
        if self.request.method in ("POST", "PUT", "DELETE"):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
