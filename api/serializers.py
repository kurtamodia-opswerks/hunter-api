from rest_framework import serializers
from .models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'element', 'power']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Skill name cannot be empty.")
        return value

    def validate_power(self, value):
        if value <= 0:
            raise serializers.ValidationError("Skill power must be greater than 0.")
        return value


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
            'skills', 'power_level', 'date_joined', 'first_name', 'last_name'
        ]

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("First name cannot be empty.")
        return value

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Last name cannot be empty.")
        return value

    def validate_rank(self, value):
        valid_ranks = [choice[0] for choice in Hunter.RankChoices.choices]
        if value not in valid_ranks:
            raise serializers.ValidationError(f"Rank must be one of {valid_ranks}.")
        return value


class GuildMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Hunter
        fields = ['id', 'full_name', 'rank_display']

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username


class GuildSerializer(serializers.ModelSerializer):
    leader = serializers.PrimaryKeyRelatedField(queryset=Hunter.objects.all())
    members = GuildMemberSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()

    class Meta:
        model = Guild
        fields = ['id', 'name', 'founded_date', 'leader', 'members', 'member_count']

    def validate(self, data):
        # Only enforce on creation
        if self.instance is None:  # creation
            if 'name' not in data or not data['name'].strip():
                raise serializers.ValidationError({"name": "Guild name is required."})
            if 'leader' not in data or data['leader'] is None:
                raise serializers.ValidationError({"leader": "Guild leader is required."})
        return data


class DungeonSerializer(serializers.ModelSerializer):
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank', 'rank_display', 'location', 'is_open']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Dungeon name cannot be empty.")
        return value

    def validate_location(self, value):
        if not value.strip():
            raise serializers.ValidationError("Dungeon location cannot be empty.")
        return value


class RaidParticipationSerializer(serializers.ModelSerializer):
    hunter = HunterSerializer(read_only=True)

    class Meta:
        model = RaidParticipation
        fields = ['id', 'hunter', 'role', 'damage_dealt', 'healing_done']

    def validate_damage_dealt(self, value):
        if value < 0:
            raise serializers.ValidationError("Damage dealt cannot be negative.")
        return value

    def validate_healing_done(self, value):
        if value < 0:
            raise serializers.ValidationError("Healing done cannot be negative.")
        return value


class RaidSerializer(serializers.ModelSerializer):
    dungeon = DungeonSerializer(read_only=True)
    participations = RaidParticipationSerializer(many=True, read_only=True)
    team_strength = serializers.ReadOnlyField()

    class Meta:
        model = Raid
        fields = ['raid_id', 'name', 'dungeon', 'date', 'success', 'team_strength', 'participations']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Raid name cannot be empty.")
        return value
    
    def validate_dungeon(self, value):
        if not value.is_open:
            raise serializers.ValidationError("Cannot create raid in an closed dungeon.")
        return value
