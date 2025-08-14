import django_filters
from rest_framework import filters
from .models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation

class ActiveDungeonFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(is_open=True)

class HunterFilter(django_filters.FilterSet):
    class Meta:
        model = Hunter
        fields = {
            'rank': ['exact'],
            'username': ['icontains'],
        }

class GuildFilter(django_filters.FilterSet):
    class Meta:
        model = Guild
        fields = {
            'name': ['icontains'],
            'leader': ['exact'],
        }

class SkillFilter(django_filters.FilterSet):
    class Meta:
        model = Skill
        fields = {
            'name': ['icontains'],
            'element': ['exact'],
        }

class RaidFilter(django_filters.FilterSet):
    class Meta:
        model = Raid
        fields = {
            'name': ['icontains'],
            'date': ['exact', 'gte'],
        }

class RaidParticipationFilter(django_filters.FilterSet):
    class Meta:
        model = RaidParticipation
        fields = {
            'role': ['exact'],
            'hunter': ['exact'],
        }
