from rest_framework import serializers
from ..models import Skill

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