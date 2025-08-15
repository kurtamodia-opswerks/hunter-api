import logging
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, filters, status
from django.shortcuts import get_object_or_404
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation
from ..serializers import (
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
from ..filters import HunterFilter, GuildFilter, SkillFilter, RaidFilter, RaidParticipationFilter, ActiveDungeonFilterBackend
from ..tasks import (
    send_hunter_welcome_email,
    send_guild_invite_email,
    send_raid_notification_email,
    send_guild_creation_email
)

logger = logging.getLogger('api')

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
        logger.info("Fetching skill list")
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        logger.debug("Delaying skill queryset for simulation")
        time.sleep(2)
        qs = super().get_queryset()
        logger.debug(f"Skill queryset count: {qs.count()}")
        return qs
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method == 'POST' or self.request.method == 'PUT' or self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAuthenticated]
        logger.debug(f"SkillViewSet permissions: {self.permission_classes}")
        return super().get_permissions()
    
    def perform_create(self, serializer):
        skill = serializer.save()
        logger.info(f"Skill created: {skill.name} (Power: {skill.power})")


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
        logger.info("Fetching hunter list")
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        hunter = serializer.save()
        logger.info(f"Hunter created: {hunter.username} (ID: {hunter.id}) — Sending welcome email")
        send_hunter_welcome_email.delay(hunter.id)
    
    def get_queryset(self):
        import time
        logger.debug("Delaying hunter queryset for simulation")
        time.sleep(2)
        qs = super().get_queryset()
        logger.debug(f"Hunter queryset count: {qs.count()}")
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            logger.debug("Using HunterCreateSerializer for write operation")
            return HunterCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method in ('POST', 'PUT', 'DELETE'):
            self.permission_classes = [permissions.IsAdminUser]
        logger.debug(f"HunterViewSet permissions: {self.permission_classes}")
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
        logger.info("Fetching guild list")
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        guild = serializer.save()
        logger.info(f"Guild created: {guild.name} (ID: {guild.pk})")
        send_guild_creation_email.delay(guild.pk)

    def get_queryset(self):
        import time
        logger.debug("Delaying guild queryset for simulation")
        time.sleep(2)
        qs = super().get_queryset()
        logger.debug(f"Guild queryset count: {qs.count()}")
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            logger.debug("Using GuildCreateSerializer for write operation")
            return GuildCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method in ('POST', 'PUT', 'DELETE'):
            self.permission_classes = [permissions.IsAdminUser]
        logger.debug(f"GuildViewSet permissions: {self.permission_classes}")
        return super().get_permissions()

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
        logger.info("Fetching dungeon list")
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        logger.debug("Delaying dungeon queryset for simulation")
        time.sleep(2)
        qs = super().get_queryset()
        logger.debug(f"Dungeon queryset count: {qs.count()}")
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            logger.debug("Using DungeonCreateSerializer for write operation")
            return DungeonCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        dungeon = serializer.save()
        logger.info(f"Dungeon created: {dungeon.name} (Rank: {dungeon.rank})")


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
        logger.info(f"Fetching raid participations for user {request.user}")
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        logger.debug("Delaying raid participation queryset for simulation")
        time.sleep(2)
        
        qs = super().get_queryset()
        
        if not self.request.user.is_staff:
            logger.debug(f"Filtering participations for hunter {self.request.user}")
            qs = qs.filter(hunter=self.request.user)
        
        logger.debug(f"Raid participation queryset count: {qs.count()}")
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            logger.debug("Using RaidParticipationCreateSerializer for write operation")
            return RaidParticipationCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.IsAuthenticated]
        if self.request.method in ('POST', 'PUT', 'DELETE'):
            self.permission_classes = [permissions.IsAdminUser]
        logger.debug(f"RaidParticipationViewSet permissions: {self.permission_classes}")
        return super().get_permissions()
    
    def perform_create(self, serializer):
        participation = serializer.save()
        logger.info(
            f"Raid participation created: Hunter {participation.hunter} "
            f"in Raid {participation.raid} — Damage: {participation.damage_dealt}, Healing: {participation.healing_done}"
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
        logger.info("Fetching raid list")
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        raid = serializer.save()
        logger.info(f"Raid created: {raid.name} (ID: {raid.raid_id}) — Sending notification email")
        send_raid_notification_email.delay(raid.raid_id)
    
    def get_queryset(self):
        import time
        logger.debug("Delaying raid queryset for simulation")
        time.sleep(2)
        qs = super().get_queryset()
        logger.debug(f"Raid queryset count: {qs.count()}")
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            logger.debug("Using RaidCreateSerializer for write operation")
            return RaidCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method in ('POST', 'PUT', 'DELETE'):
            self.permission_classes = [permissions.IsAdminUser]
        logger.debug(f"RaidViewSet permissions: {self.permission_classes}")
        return super().get_permissions()

