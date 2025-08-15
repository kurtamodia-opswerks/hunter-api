import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from ..models import Guild, Raid
from ..serializers import (
    GuildInviteSerializer,
    RaidInviteSerializer
)
from ..tasks import (
    send_guild_invite_email,
    send_raid_participation_invite_email
)

logger = logging.getLogger('api')

class GuildInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = GuildInviteSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Guild invite validation failed: {serializer.errors}")
            serializer.is_valid(raise_exception=True)

        hunter_id = serializer.validated_data['hunter_id']
        guild_id = serializer.validated_data['guild_id']

        guild = Guild.objects.get(pk=guild_id)
        if request.user != guild.leader:
            logger.warning(f"Unauthorized guild invite attempt by {request.user}")
            return Response(
                {"error": "You do not have permission to invite hunters to this guild."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Trigger Celery task
        logger.info(f"Guild invite sent: Hunter ID {hunter_id} to Guild {guild.name} (ID: {guild_id}) by {request.user}")
        task = send_guild_invite_email.delay(hunter_id, guild_id)
        return Response(
            {"message": "Guild invite email is being sent.", "task_id": task.id},
            status=status.HTTP_202_ACCEPTED
        )
    
class RaidInviteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = RaidInviteSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Raid invite validation failed: {serializer.errors}")
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

        # Just log the invite
        logger.info(
            f"Raid invite sent: Hunter ID {hunter_id} to Raid '{raid.name}' "
            f"(ID: {raid_id}) by {request.user}"
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

