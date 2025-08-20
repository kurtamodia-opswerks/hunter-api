from rest_framework import serializers
from api.models import RaidParticipation, Hunter, Raid

# For better nested creation inside raid serializer
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

class RaidParticipationSerializer(serializers.ModelSerializer):
    # Read-only fields
    raid_id = serializers.IntegerField(source='raid.id', read_only=True)
    hunter_id = serializers.IntegerField(source='hunter.id', read_only=True)
    full_name = serializers.CharField(source='hunter.full_name', read_only=True)
    hunter_rank = serializers.CharField(source='hunter.rank_display', read_only=True)

    # Write-only fields (for input)
    raid = serializers.PrimaryKeyRelatedField(
        queryset=Raid.objects.all(), write_only=True
    )
    hunter = serializers.PrimaryKeyRelatedField(
        queryset=Hunter.objects.all(), write_only=True
    )

    class Meta:
        model = RaidParticipation
        fields = [
            'id', 
            'raid_id', 'hunter_id',  # readonly
            'raid', 'hunter',        # writeonly
            'full_name', 'hunter_rank',
            'role'
        ]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)  # 👈 allow dynamic fields
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            for field_name in list(self.fields):
                if field_name not in allowed:
                    self.fields.pop(field_name)

    def validate_role(self, value):
        valid_roles = [r[0] for r in RaidParticipation.RoleChoices.choices]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of {valid_roles}.")
        return value

    