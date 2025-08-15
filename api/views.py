from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, filters, status
from django.shortcuts import get_object_or_404
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from .models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation
from .serializers import (
    HunterSerializer,
    GuildSerializer,
    SkillSerializer,
    DungeonSerializer,
    RaidSerializer,
    RaidParticipationSerializer,
    HunterCreateSerializer,
    GuildCreateSerializer,
    DungeonCreateSerializer,
    RaidCreateSerializer,
    RaidParticipationCreateSerializer,
    GuildInviteSerializer
)
from .filters import HunterFilter, GuildFilter, SkillFilter, RaidFilter, RaidParticipationFilter, ActiveDungeonFilterBackend
from .tasks import (
    send_hunter_welcome_email,
    send_guild_invite_email,
    send_raid_notification_email
)

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SkillFilter
    search_fields = ['name']
    ordering_fields = ['name', 'power']

    @method_decorator(cache_page(60 * 15, key_prefix='skill_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class HunterViewSet(viewsets.ModelViewSet):
    queryset = Hunter.objects.select_related('guild') \
        .prefetch_related('skills', 'completed_raids', 'participations', 'participations__raid') \
        .all()
    serializer_class = HunterSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HunterFilter
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'rank']

    @method_decorator(cache_page(60 * 15, key_prefix='hunter_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        hunter = serializer.save()
        send_hunter_welcome_email.delay(hunter.id)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return HunterCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

class GuildViewSet(viewsets.ModelViewSet):
    queryset = Guild.objects.select_related('leader') \
        .prefetch_related(
            'members',
            'members__skills',
            'members__participations',
            'members__participations__raid'
        ).all()
    serializer_class = GuildSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GuildFilter
    search_fields = ['name']
    ordering_fields = ['name', 'founded_date']

    @method_decorator(cache_page(60 * 15, key_prefix='guild_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return GuildCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

class GuildInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = GuildInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hunter_id = serializer.validated_data['hunter_id']
        guild_id = serializer.validated_data['guild_id']

        # Optional: check permissions (guild leader or admin)
        guild = Guild.objects.get(pk=guild_id)
        if request.user != guild.leader:
            return Response(
                {"error": "You do not have permission to invite hunters to this guild."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Trigger Celery task
        task = send_guild_invite_email.delay(hunter_id, guild_id)
        return Response(
            {"message": "Guild invite email is being sent.", "task_id": task.id},
            status=status.HTTP_202_ACCEPTED
        )

class DungeonViewSet(viewsets.ModelViewSet):
    queryset = Dungeon.objects.prefetch_related(
        'raids', 'raids__participations', 'raids__participations__hunter'
    ).all()
    serializer_class = DungeonSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [ActiveDungeonFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'rank']

    @method_decorator(cache_page(60 * 15, key_prefix='dungeon_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return DungeonCreateSerializer
        return super().get_serializer_class()

class RaidParticipationViewSet(viewsets.ModelViewSet):
    queryset = RaidParticipation.objects.select_related('raid', 'hunter').all()
    serializer_class = RaidParticipationSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RaidParticipationFilter
    ordering_fields = ['damage_dealt', 'healing_done']

    @method_decorator(cache_page(60 * 15, key_prefix='participation_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        
        qs = super().get_queryset()
        
        # Only show participations for the authenticated hunter if not staff
        if not self.request.user.is_staff:
            qs = qs.filter(hunter=self.request.user)
        
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return RaidParticipationCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.IsAuthenticated]
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()


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
        import time
        time.sleep(2)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return RaidCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
