from rest_framework import serializers
from api.models import Hunter, Guild

# For better reading only
class GuildMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hunter
        fields = ['id', 'full_name', 'rank_display']

class GuildSerializer(serializers.ModelSerializer):
    leader_read_only = GuildMemberSerializer(read_only=True)
    leader_write_only = serializers.PrimaryKeyRelatedField(queryset=Hunter.objects.all(), write_only=True)
    members = GuildMemberSerializer(many=True)

    class Meta:
        model = Guild
        fields = ['id', 'name', 'founded_date', 'leader_read_only', 'leader_write_only', 'members', 'member_count']
        read_only_fields = ['id', 'founded_date', 'leader_read_only', 'member_count', 'members']
        extra_kwargs = {
            'leader_write_only': {'write_only': True}
        }

    def validate(self, data):
        if not data.get('name', '').strip():
            raise serializers.ValidationError({"name": "Guild name is required."})
        if not data.get('leader_write_only'):
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
