from django.contrib import admin
from .models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation

class HunterInline(admin.TabularInline):
    model = Hunter
    extra = 1  

class RaidParticipationInline(admin.TabularInline):
    model = RaidParticipation
    extra = 1

class GuildAdmin(admin.ModelAdmin):
    inlines = [HunterInline]

class RaidAdmin(admin.ModelAdmin):
    inlines = [RaidParticipationInline]

# Register models
admin.site.register(Hunter)
admin.site.register(Guild, GuildAdmin)
admin.site.register(Skill)
admin.site.register(Dungeon)
admin.site.register(Raid, RaidAdmin)
admin.site.register(RaidParticipation)
