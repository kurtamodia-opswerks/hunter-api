from rest_framework import serializers
from api.models import Raid, Hunter, RaidParticipation, Dungeon
from api.serializers.dungeon import DungeonBriefSerializer
from api.serializers.raid_participation import RaidParticipationNestedSerializer, RaidParticipationSerializer

class RaidSerializer(serializers.ModelSerializer):
    dungeon = serializers.PrimaryKeyRelatedField(queryset=Dungeon.objects.filter(is_open=True))
    dungeon_info = DungeonBriefSerializer(source='dungeon', read_only=True)
    # participations_info = RaidParticipationSerializer(
    #     many=True, 
    #     read_only=True, 
    #     source='participations'  
    # )
    participations_info = serializers.SerializerMethodField()
    participations_create = RaidParticipationNestedSerializer(many=True, write_only=True)

    class Meta:
        model = Raid
        fields = [
            'id', 'name', 'dungeon', 'dungeon_info',
            'date', 'success', 'team_strength',
            'participations_info', 'participations_create'
        ]
        read_only_fields = ['id', 'dungeon_info', 'team_strength', 'participations_info']

    def get_participations_info(self, obj):
        # Use the same serializer but only keep clean fields
        serializer = RaidParticipationSerializer(
            obj.participations.all(), 
            many=True, 
            fields=['full_name', 'hunter_rank', 'role']
        )
        return serializer.data

    def create(self, validated_data):
        participations_data = validated_data.pop('participations_create', [])
        raid = Raid.objects.create(**validated_data)

        # Use validated data directly
        for part_data in participations_data:
            hunter_id = part_data['hunter_id']
            role = part_data['role']
            hunter = Hunter.objects.get(pk=hunter_id)
            RaidParticipation.objects.create(
                raid=raid,
                hunter=hunter,
                role=role
            )

        return raid