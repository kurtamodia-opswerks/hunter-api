from rest_framework import serializers
from api.models import Dungeon

class DungeonSerializer(serializers.ModelSerializer):
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank_display', 'rank', 'location', 'is_open']
        read_only_fields = ['id', 'rank_display']
        extra_kwargs = {
            'rank': {'write_only': True}
        }

    def validate(self, data):
        if not data.get('name', '').strip():
            raise serializers.ValidationError({"name": "Dungeon name is required."})
        if not data.get('location', '').strip():
            raise serializers.ValidationError({"location": "Dungeon location is required."})
        return data

class DungeonBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank']

