import django_filters
from api.models import Dungeon, Guild, Hunter, Raid, RaidParticipation, Skill
from rest_framework import filters


class DungeonFilter(django_filters.FilterSet):
    class Meta:
        model = Dungeon
        fields = {
            "name": ["icontains"],
            "location": ["icontains"],
            "rank": ["exact", "gte", "lte"],
        }


class HunterFilter(django_filters.FilterSet):
    guild_isnull = django_filters.BooleanFilter(
        field_name="guild", lookup_expr="isnull"
    )

    class Meta:
        model = Hunter
        fields = {
            "rank": ["exact"],
            "guild": ["exact"],
        }


class GuildFilter(django_filters.FilterSet):
    class Meta:
        model = Guild
        fields = {
            "name": ["icontains"],
            "leader": ["exact"],
        }


class SkillFilter(django_filters.FilterSet):
    class Meta:
        model = Skill
        fields = {
            "name": ["icontains"],
            "element": ["exact"],
        }


class RaidFilter(django_filters.FilterSet):
    class Meta:
        model = Raid
        fields = {
            "name": ["icontains"],
            "date": ["exact", "gte"],
        }


class RaidParticipationFilter(django_filters.FilterSet):
    class Meta:
        model = RaidParticipation
        fields = {
            "role": ["exact"],
            "hunter": ["exact"],
        }
