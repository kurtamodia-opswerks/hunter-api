from api.models import Guild
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["is_admin"] = user.is_staff  # or user.is_superuser
        token["username"] = user.username
        token["is_leader"] = Guild.objects.filter(leader=user).exists()
        return token
