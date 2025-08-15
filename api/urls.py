from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from rest_framework.routers import DefaultRouter
from .views import (
    HunterViewSet,
    GuildViewSet,
    GuildInviteView,
    SkillViewSet,
    DungeonViewSet,
    RaidViewSet,
    RaidParticipationViewSet,
    RaidInviteView
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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/guild-invite/', GuildInviteView.as_view(), name='guild-invite'),
    path('api/raid-invite/', RaidInviteView.as_view(), name='raid-invite'),
]
