from rest_framework import viewsets, permissions
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
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
    RaidParticipationCreateSerializer
)

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


class HunterViewSet(viewsets.ModelViewSet):
    queryset = Hunter.objects.select_related('guild') \
        .prefetch_related('skills', 'completed_raids', 'participations', 'participations__raid') \
        .all()
    serializer_class = HunterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return HunterCreateSerializer
        return super().get_serializer_class()


class GuildViewSet(viewsets.ModelViewSet):
    queryset = Guild.objects.select_related('leader') \
        .prefetch_related(
            'members',
            'members__skills',
            'members__participations',
            'members__participations__raid'
        ).all()
    serializer_class = GuildSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return GuildCreateSerializer
        return super().get_serializer_class()


class DungeonViewSet(viewsets.ModelViewSet):
    queryset = Dungeon.objects.prefetch_related(
        'raids', 'raids__participations', 'raids__participations__hunter'
    ).all()
    serializer_class = DungeonSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return DungeonCreateSerializer
        return super().get_serializer_class()


class RaidParticipationViewSet(viewsets.ModelViewSet):
    queryset = RaidParticipation.objects.select_related('raid', 'hunter').all()
    serializer_class = RaidParticipationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return RaidParticipationCreateSerializer
        return super().get_serializer_class()


class RaidViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.select_related('dungeon') \
        .prefetch_related(
            'participations',
            'participations__hunter',
            'participations__hunter__skills'
        ).all()
    serializer_class = RaidSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return RaidCreateSerializer
        return super().get_serializer_class()
