from rest_framework import serializers
from api.models import RaidParticipation, Hunter, Raid

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
    
class RaidParticipationNestedSerializer(serializers.ModelSerializer):
    hunter_id = serializers.IntegerField()
    
    class Meta:
        model = RaidParticipation
        fields = ['hunter_id', 'role']

    def validate_hunter_id(self, value):
        if not Hunter.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Hunter does not exist.")
        return value

    def validate_role(self, value):
        valid_roles = [r[0] for r in RaidParticipation.RoleChoices.choices]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of {valid_roles}.")
        return value
    
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