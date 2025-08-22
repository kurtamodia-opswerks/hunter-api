from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from api.models import Hunter, Guild, Dungeon, Raid, RaidParticipation, Skill

def clear_cache(pattern: str):
    cache.delete_pattern(pattern)
    print(f"Cache cleared for pattern: {pattern}")

@receiver([post_save, post_delete], sender=Hunter)
def invalidate_hunter_cache(sender, instance, **kwargs):
    clear_cache("*hunter_list*")

@receiver([post_save, post_delete], sender=Guild)
def invalidate_guild_cache(sender, instance, **kwargs):
    clear_cache("*guild_list*")

@receiver([post_save, post_delete], sender=Dungeon)
def invalidate_dungeon_cache(sender, instance, **kwargs):
    clear_cache("*dungeon_list*")

@receiver([post_save, post_delete], sender=Raid)
def invalidate_raid_cache(sender, instance, **kwargs):
    clear_cache("*raid_list*")

@receiver([post_save, post_delete], sender=RaidParticipation)
def invalidate_raid_participation_cache(sender, instance, **kwargs):
    clear_cache("*participation_list*")


@receiver([post_save, post_delete], sender=Skill)
def invalidate_skill_cache(sender, instance, **kwargs):
    clear_cache("*skill_list*")

# Add the leader as a member when a guild is created
@receiver(post_save, sender=Guild)
def add_leader_as_member(sender, instance, created, **kwargs):
    if created and instance.leader:
        instance.members.add(instance.leader)
