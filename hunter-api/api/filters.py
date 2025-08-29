import django_filters
from api.models import Dungeon, Guild, Hunter, Raid, RaidParticipation, Skill
from rest_framework import filters


class ActiveDungeonFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(is_open=True)


class HunterFilter(django_filters.FilterSet):
    class Meta:
        model = Hunter
        fields = {
            "rank": ["exact"],
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
