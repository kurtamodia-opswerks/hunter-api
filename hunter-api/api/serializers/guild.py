from api.models import Guild, Hunter
from rest_framework import serializers


# For better reading only
class GuildMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hunter
        fields = ["id", "full_name", "rank_display"]


class GuildSerializer(serializers.ModelSerializer):
    leader = serializers.PrimaryKeyRelatedField(
        queryset=Hunter.objects.all(), write_only=True
    )
    leader_display = GuildMemberSerializer(source="leader", read_only=True)
    members = GuildMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Guild
        fields = [
            "id",
            "name",
            "founded_date",
            "leader",
            "leader_display",
            "members",
            "member_count",
        ]
        read_only_fields = [
            "id",
            "founded_date",
            "leader_display",
            "member_count",
            "members",
        ]

    def validate(self, data):
        if not data.get("name", "").strip():
            raise serializers.ValidationError({"name": "Guild name is required."})
        if not data.get("leader"):
            raise serializers.ValidationError({"leader": "Guild leader is required."})
        return data


class GuildInviteSerializer(serializers.Serializer):
    hunter_id = serializers.IntegerField()
    guild_id = serializers.IntegerField()

    def validate_hunter_id(self, value):
        if not Hunter.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Hunter with this ID does not exist.")
        return value

    def validate_guild_id(self, value):
        if not Guild.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Guild with this ID does not exist.")
        return value
