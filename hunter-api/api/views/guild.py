import time

from api.filters import GuildFilter
from api.models import Guild
from api.serializers import GuildInviteSerializer, GuildSerializer
from api.tasks import send_guild_creation_email, send_guild_invite_email
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView


class GuildViewSet(viewsets.ModelViewSet):
    queryset = (
        Guild.objects.select_related("leader")
        .prefetch_related(
            "members",
            "members__skills",
            "members__participations",
            "members__participations__raid",
        )
        .all()
    )
    serializer_class = GuildSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = GuildFilter
    search_fields = ["name"]
    ordering_fields = ["name", "founded_date"]

    @method_decorator(cache_page(60 * 15, key_prefix="guild_list"))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        guild = serializer.save()
        send_guild_creation_email.delay(guild.pk)

    def get_queryset(self):
        time.sleep(2)
        qs = super().get_queryset().order_by("founded_date", "name")
        return qs

    def get_permissions(self):
        self.permission_classes = [permissions.IsAuthenticated]
        if self.request.method in ("POST", "PUT", "DELETE"):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()


class GuildInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = GuildInviteSerializer(data=request.data)
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)

        hunter_id = serializer.validated_data["hunter_id"]
        guild_id = serializer.validated_data["guild_id"]

        guild = Guild.objects.get(pk=guild_id)
        if request.user != guild.leader:
            return Response(
                {
                    "error": "You do not have permission to invite hunters to this guild."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Trigger Celery task
        task = send_guild_invite_email.delay(hunter_id, guild_id)
        return Response(
            {"message": "Guild invite email is being sent.", "task_id": task.id},
            status=status.HTTP_202_ACCEPTED,
        )
