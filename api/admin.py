from django.contrib import admin
from .models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation

# Inline Hunters in a Guild
class HunterInline(admin.TabularInline):
    model = Hunter
    extra = 1  # how many blank forms to show

# Inline RaidParticipation in a Raid
class RaidParticipationInline(admin.TabularInline):
    model = RaidParticipation
    extra = 1

# Guild admin with inline hunters
class GuildAdmin(admin.ModelAdmin):
    inlines = [HunterInline]

# Raid admin with inline participation
class RaidAdmin(admin.ModelAdmin):
    inlines = [RaidParticipationInline]

# Register models
admin.site.register(Hunter)
admin.site.register(Guild, GuildAdmin)
admin.site.register(Skill)
admin.site.register(Dungeon)
admin.site.register(Raid, RaidAdmin)
admin.site.register(RaidParticipation)
