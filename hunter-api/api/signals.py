from api.models import Dungeon, Guild, Hunter, Raid, RaidParticipation, Skill
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


def clear_cache(pattern: str):
    cache.delete_pattern(pattern)
    print(f"Cache cleared for pattern: {pattern}")


@receiver([post_save, post_delete], sender=Hunter)
def invalidate_hunter_cache(sender, instance, **kwargs):
    clear_cache("*hunter_list*")
    clear_cache("*participation_list*")
    clear_cache("*guild_list*")
    clear_cache("*raid_list*")
    clear_cache("*skill_list*")


@receiver([post_save, post_delete], sender=Guild)
def invalidate_guild_cache(sender, instance, **kwargs):
    clear_cache("*guild_list*")
    clear_cache("*hunter_list*")


@receiver([post_save, post_delete], sender=Dungeon)
def invalidate_dungeon_cache(sender, instance, **kwargs):
    clear_cache("*dungeon_list*")
    clear_cache("*raid_list*")


@receiver([post_save, post_delete], sender=Raid)
def invalidate_raid_cache(sender, instance, **kwargs):
    clear_cache("*raid_list*")
    clear_cache("*participation_list*")
    clear_cache("*hunter_list*")


@receiver([post_save, post_delete], sender=RaidParticipation)
def invalidate_raid_participation_cache(sender, instance, **kwargs):
    clear_cache("*participation_list*")
    clear_cache("*raid_list*")
    clear_cache("*hunter_list*")


@receiver([post_save, post_delete], sender=Skill)
def invalidate_skill_cache(sender, instance, **kwargs):
    clear_cache("*skill_list*")
    clear_cache("*hunter_list*")


# Add the leader as a member when a guild is created
@receiver(post_save, sender=Guild)
def add_leader_as_member(sender, instance, created, **kwargs):
    if created and instance.leader:
        instance.members.add(instance.leader)
