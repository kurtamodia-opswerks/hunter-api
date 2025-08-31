from api.views import (
    DungeonViewSet,
    GuildInviteView,
    GuildViewSet,
    HunterViewSet,
    RaidParticipationViewSet,
    RaidViewSet,
    SkillViewSet,
    VerifyPasswordView,
)
from api.views.token import CustomTokenObtainPairView
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# Create a router and register viewsets
router = DefaultRouter()
router.register("hunters", HunterViewSet)
router.register("guilds", GuildViewSet)
router.register("skills", SkillViewSet)
router.register("dungeons", DungeonViewSet)
router.register("raids", RaidViewSet)
router.register("raid-participations", RaidParticipationViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path("api/guild-invite/", GuildInviteView.as_view(), name="guild-invite"),
    path("api/verify-password/", VerifyPasswordView.as_view(), name="verify-password"),
]
