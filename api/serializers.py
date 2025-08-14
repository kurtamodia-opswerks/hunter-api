from rest_framework import serializers
from .models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'element', 'power']


class HunterSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    guild = serializers.StringRelatedField()
    power_level = serializers.ReadOnlyField()
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Hunter
        fields = [
            'id', 'full_name', 'rank_display', 'guild',
            'skills', 'power_level', 'date_joined'
        ]

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name

class GuildMemberSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Hunter
        fields = ['id', 'full_name', 'rank', 'skills', 'power_level']

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

class GuildSerializer(serializers.ModelSerializer):
    leader = HunterSerializer(read_only=True)
    members = GuildMemberSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()

    class Meta:
        model = Guild
        fields = ['id', 'name', 'founded_date', 'leader', 'members', 'member_count']

class DungeonSerializer(serializers.ModelSerializer):
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank', 'rank_display', 'location', 'is_open']


class RaidParticipationSerializer(serializers.ModelSerializer):
    hunter = HunterSerializer(read_only=True)

    class Meta:
        model = RaidParticipation
        fields = ['id', 'hunter', 'role', 'damage_dealt', 'healing_done']


class RaidSerializer(serializers.ModelSerializer):
    dungeon = DungeonSerializer(read_only=True)
    participations = RaidParticipationSerializer(many=True, read_only=True)
    team_strength = serializers.ReadOnlyField()

    class Meta:
        model = Raid
        fields = ['raid_id', 'name', 'dungeon', 'date', 'success', 'team_strength', 'participations']
