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
    guild_name = serializers.CharField(source="guild.name", read_only=True)

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
            "guild_name",
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
            "password": {
                "write_only": True,
                "required": False,
            },  # <-- not required by default
        }

    def create(self, validated_data):
        skills = validated_data.pop("skills", [])
        guild = validated_data.pop("guild", None)

        user = Hunter(**validated_data)
        user.set_password(
            validated_data["password"]
        )  # safe because password is required in validate()
        user.save()

        if skills:
            user.skills.set(skills)
        if guild:
            user.guild = guild
            user.save()

        return user

    def update(self, instance, validated_data):
        skills = validated_data.pop("skills", None)
        guild = validated_data.pop("guild", None)
        password = validated_data.pop("password", None)

        # Normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Password: only update if non-empty string
        if password is not None and password.strip():
            instance.set_password(password)

        instance.save()

        # Skills: explicit [] clears them, None means "not provided"
        if skills is not None:
            instance.skills.set(skills)

        # Guild: explicit null clears it, None means "not provided"
        if "guild" in self.initial_data:  # ensures user explicitly sent guild
            instance.guild = guild  # can be real Guild or None
            instance.save()

        return instance

    def validate(self, data):
        # Normalize password empty string → drop it
        if "password" in data and data["password"] == "":
            data.pop("password")

        # Validation only when creating
        if self.instance is None:
            if not data.get("first_name", "").strip():
                raise serializers.ValidationError(
                    {"first_name": "First name is required."}
                )
            if not data.get("last_name", "").strip():
                raise serializers.ValidationError(
                    {"last_name": "Last name is required."}
                )
            if not data.get("password", "").strip():
                raise serializers.ValidationError(
                    {"password": "Password is required on create."}
                )
            if not data.get("username", "").strip():
                raise serializers.ValidationError(
                    {"username": "Username is required on create."}
                )
        return data
