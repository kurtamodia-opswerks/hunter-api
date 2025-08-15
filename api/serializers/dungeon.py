from rest_framework import serializers
from ..models import Dungeon

class DungeonSerializer(serializers.ModelSerializer):
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)

    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank_display', 'location', 'is_open']

class DungeonBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dungeon
        fields = ['id', 'name', 'rank']

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