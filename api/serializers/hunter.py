from rest_framework import serializers
from .skill import SkillSerializer
from api.models import Hunter, Skill, Guild

class HunterSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    guild = serializers.StringRelatedField()
    power_level = serializers.SerializerMethodField()
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Hunter
        fields = [
            'id', 'date_joined', 'full_name', 'rank_display', 'email', 'guild',
            'skills', 'power_level'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_power_level(self, obj):
        return obj.power_level
    
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
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if self.instance is None:
            if not data.get('first_name', '').strip():
                raise serializers.ValidationError({"first_name": "First name is required."})
            if not data.get('last_name', '').strip():
                raise serializers.ValidationError({"last_name": "Last name is required."})
            if data.get('rank') not in [r[0] for r in Hunter.RankChoices.choices]:
                raise serializers.ValidationError({"rank": "Valid rank is required."})
        return data
    
    def create(self, validated_data):
            skills = validated_data.pop('skills', [])
            guild = validated_data.pop('guild', None)

            user = Hunter(**validated_data)

            user.set_password(validated_data['password'])
            user.save()

            if skills:
                user.skills.set(skills)
            if guild:
                user.guild = guild
                user.save()

            return user