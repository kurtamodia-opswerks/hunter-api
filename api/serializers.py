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
    power_level = serializers.SerializerMethodField()
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Hunter
        fields = [
            'id', 'date_joined', 'full_name', 'rank_display', 'guild',
            'skills', 'power_level'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_power_level(self, obj):
        return obj.power_level

class GuildMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Hunter
        fields = ['id', 'full_name', 'rank_display']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class GuildSerializer(serializers.ModelSerializer):
    leader = GuildMemberSerializer(read_only=True)
    members = GuildMemberSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()

    class Meta:
        model = Guild
        fields = ['id', 'name', 'founded_date', 'leader', 'members', 'member_count']

class DungeonSerializer(serializers.ModelSerializer):
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank_display', 'location', 'is_open']

class ParticipationSerializer(serializers.ModelSerializer):
    hunter_id = serializers.IntegerField(source='hunter.id', read_only=True)
    full_name = serializers.SerializerMethodField()
    hunter_rank = serializers.CharField(source='hunter.get_rank_display', read_only=True)

    class Meta:
        model = RaidParticipation
        fields = ['hunter_id', 'full_name', 'hunter_rank']

    def get_full_name(self, obj):
        return f"{obj.hunter.first_name} {obj.hunter.last_name}".strip()

class RaidParticipationSerializer(serializers.ModelSerializer):
    raid_id = serializers.ReadOnlyField(source='raid.raid_id')
    hunter_id = serializers.IntegerField(source='hunter.id', read_only=True)
    hunter_full_name = serializers.SerializerMethodField()
    hunter_rank = serializers.CharField(source='hunter.get_rank_display', read_only=True)

    class Meta:
        model = RaidParticipation
        fields = ['id', 'raid_id', 'hunter_id', 'hunter_full_name', 'hunter_rank', 'role', 'damage_dealt', 'healing_done']

    def get_hunter_full_name(self, obj):
        return f"{obj.hunter.first_name} {obj.hunter.last_name}".strip()

    def validate_damage_dealt(self, value):
        if value < 0:
            raise serializers.ValidationError("Damage dealt cannot be negative.")
        return value

    def validate_healing_done(self, value):
        if value < 0:
            raise serializers.ValidationError("Healing done cannot be negative.")
        return value

    def validate_role(self, value):
        valid_roles = [r[0] for r in RaidParticipation.RoleChoices.choices]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of {valid_roles}.")
        return value

class DungeonBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank']

class RaidSerializer(serializers.ModelSerializer):
    dungeon_info = DungeonBriefSerializer(source='dungeon', read_only=True)
    participations = ParticipationSerializer(many=True, read_only=True)
    team_strength = serializers.ReadOnlyField()
    raid_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Raid
        fields = ['raid_id', 'name', 'dungeon_info', 'date', 'success', 'team_strength', 'participations']

class HunterCreateSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), required=False
    )
    guild = serializers.PrimaryKeyRelatedField(
        queryset=Guild.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Hunter
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'rank', 'skills', 'guild']

    def validate(self, data):
        if self.instance is None:
            if not data.get('first_name', '').strip():
                raise serializers.ValidationError({"first_name": "First name is required."})
            if not data.get('last_name', '').strip():
                raise serializers.ValidationError({"last_name": "Last name is required."})
            if data.get('rank') not in [r[0] for r in Hunter.RankChoices.choices]:
                raise serializers.ValidationError({"rank": "Valid rank is required."})
        return data
    
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

class DungeonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dungeon
        fields = ['name', 'rank', 'location', 'is_open']

    def validate(self, data):
        if not data.get('name', '').strip():
            raise serializers.ValidationError({"name": "Dungeon name is required."})
        if not data.get('Location', '').strip():
            raise serializers.ValidationError({"location": "Dungeon location is required."})
        return data

class RaidCreateSerializer(serializers.ModelSerializer):
    dungeon = serializers.PrimaryKeyRelatedField(queryset=Dungeon.objects.filter(is_open=True))

    class Meta:
        model = Raid
        fields = ['name', 'dungeon', 'date', 'success']

    def validate(self, data):
        if not data.get('name', '').strip():
            raise serializers.ValidationError({"name": "Raid name is required."})
        return data

class RaidParticipationCreateSerializer(serializers.ModelSerializer):
    raid_id = serializers.UUIDField(write_only=True)
    hunter_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RaidParticipation
        fields = ['raid_id', 'hunter_id', 'role', 'damage_dealt', 'healing_done']

    def validate(self, data):
        try:
            data['raid'] = Raid.objects.get(pk=data.pop('raid_id'))
        except Raid.DoesNotExist:
            raise serializers.ValidationError({"raid_id": "Raid with this ID does not exist."})

        try:
            data['hunter'] = Hunter.objects.get(pk=data.pop('hunter_id'))
        except Hunter.DoesNotExist:
            raise serializers.ValidationError({"hunter_id": "Hunter with this ID does not exist."})

        return data

    def validate_damage_dealt(self, value):
        if value < 0:
            raise serializers.ValidationError("Damage dealt cannot be negative.")
        return value

    def validate_healing_done(self, value):
        if value < 0:
            raise serializers.ValidationError("Healing done cannot be negative.")
        return value

    def validate_role(self, value):
        valid_roles = [r[0] for r in RaidParticipation.RoleChoices.choices]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of {valid_roles}.")
        return value