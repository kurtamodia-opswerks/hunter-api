from rest_framework import serializers
from api.models import Raid, Hunter, RaidParticipation, Dungeon
from api.serializers.dungeon import DungeonBriefSerializer
from api.serializers.raid_participation import ParticipationSerializer, RaidParticipationNestedSerializer

class RaidSerializer(serializers.ModelSerializer):
    dungeon_info = DungeonBriefSerializer(source='dungeon', read_only=True)
    participations = ParticipationSerializer(many=True, read_only=True)
    team_strength = serializers.ReadOnlyField()

    class Meta:
        model = Raid
        fields = ['id', 'name', 'dungeon_info', 'date', 'success', 'team_strength', 'participations']

class RaidCreateSerializer(serializers.ModelSerializer):
    dungeon = serializers.PrimaryKeyRelatedField(queryset=Dungeon.objects.filter(is_open=True))
    participations = RaidParticipationNestedSerializer(many=True, required=True)

    class Meta:
        model = Raid
        fields = ['name', 'dungeon', 'date', 'success', 'participations']

    def create(self, validated_data):
        participations_data = validated_data.pop('participations')
        raid = Raid.objects.create(**validated_data)
        
        # Create participations
        for part_data in participations_data:
            hunter = Hunter.objects.get(pk=part_data.pop('hunter_id'))
            RaidParticipation.objects.create(raid=raid, hunter=hunter, **part_data)
        
        return raid


class RaidInviteSerializer(serializers.Serializer):
    hunter_id = serializers.IntegerField()

    def validate_hunter_id(self, value):
        if not Hunter.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Hunter with this ID does not exist.")
        return value

    def validate_id(self, value):
        if not Raid.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Raid with this ID does not exist.")
        return value
