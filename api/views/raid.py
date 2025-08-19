import time
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from api.models import Raid
from api.serializers import (
    RaidSerializer,
    RaidCreateSerializer,
    RaidInviteSerializer
)
from api.filters import RaidFilter
from api.tasks import (
    send_raid_notification_email,
    send_raid_participation_invite_email
)



class RaidViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.select_related('dungeon') \
        .prefetch_related(
            'participations',
            'participations__hunter',
            'participations__hunter__skills'
        ).all()
    serializer_class = RaidSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RaidFilter
    search_fields = ['name']
    ordering_fields = ['date', 'name']

    @method_decorator(cache_page(60 * 15, key_prefix='raid_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        raid = serializer.save()
        send_raid_notification_email.delay(raid.raid_id)
    
    def get_queryset(self):
        time.sleep(2)
        qs = super().get_queryset()
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            return RaidCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method in ('POST', 'PUT', 'DELETE'):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
    






    
class RaidInviteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = RaidInviteSerializer(data=request.data)
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)

        hunter_id = serializer.validated_data['hunter_id']
        raid_id = serializer.validated_data['raid_id']

        try:
            raid = Raid.objects.get(pk=raid_id)
        except Raid.DoesNotExist:
            return Response(
                {"error": f"Raid with id {raid_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Trigger Celery task
        task = send_raid_participation_invite_email.delay(raid_id, hunter_id)

        return Response(
            {
                "message": "Raid invite email is being sent.",
                "task_id": task.id
            },
            status=status.HTTP_202_ACCEPTED
        )

