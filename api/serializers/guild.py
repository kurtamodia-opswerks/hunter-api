from rest_framework import serializers
from ..models import Hunter, Guild

class GuildMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Hunter
        fields = ['id', 'full_name', 'rank_display']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class GuildSerializer(serializers.ModelSerializer):
    leader = GuildMemberSerializer(read_only=True)
    members = GuildMemberSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()

    class Meta:
        model = Guild
        fields = ['id', 'name', 'founded_date', 'leader', 'members', 'member_count']

class GuildCreateSerializer(serializers.ModelSerializer):
    leader = serializers.PrimaryKeyRelatedField(queryset=Hunter.objects.all())

    class Meta:
        model = Guild
        fields = ['name', 'leader']

    def validate(self, data):
        if not data.get('name', '').strip():
            raise serializers.ValidationError({"name": "Guild name is required."})
        if not data.get('leader'):
            raise serializers.ValidationError({"leader": "Guild leader is required."})
        return data