from api.models import Guild, Hunter, Skill
from rest_framework import serializers

from .skill import SkillSerializer


class HunterSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), required=False
    )
    guild = serializers.PrimaryKeyRelatedField(
        queryset=Guild.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Hunter
        fields = [
            "id",
            "date_joined",
            "full_name",
            "rank_display",
            "email",
            "guild",
            "skills",
            "power_level",
            "first_name",
            "last_name",
            "username",
            "password",
            "email",
            "rank",
            "skills",
            "guild",
            "raid_count",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "full_name",
            "rank_display",
            "power_level",
            "raid_count",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "rank": {"write_only": True},
            "first_name": {"write_only": True},
            "last_name": {"write_only": True},
            "username": {"write_only": True},
        }

    def create(self, validated_data):
        skills = validated_data.pop("skills", [])
        guild = validated_data.pop("guild", None)

        user = Hunter(**validated_data)

        user.set_password(validated_data["password"])
        user.save()

        if skills:
            user.skills.set(skills)
        if guild:
            user.guild = guild
            user.save()

        return user

    def validate(self, data):
        if self.instance is None:
            if not data.get("first_name", "").strip():
                raise serializers.ValidationError(
                    {"first_name": "First name is required."}
                )
            if not data.get("last_name", "").strip():
                raise serializers.ValidationError(
                    {"last_name": "Last name is required."}
                )
            if data.get("rank") not in [r[0] for r in Hunter.RankChoices.choices]:
                raise serializers.ValidationError({"rank": "Valid rank is required."})
        return data
