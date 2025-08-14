from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HunterViewSet,
    GuildViewSet,
    SkillViewSet,
    DungeonViewSet,
    RaidViewSet,
    RaidParticipationViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register('hunters', HunterViewSet)
router.register('guilds', GuildViewSet)
router.register('skills', SkillViewSet)
router.register('dungeons', DungeonViewSet)
router.register('raids', RaidViewSet)
router.register('raid-participations', RaidParticipationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
