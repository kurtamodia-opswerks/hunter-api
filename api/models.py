from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Hunter(AbstractUser):
    class RankChoices(models.TextChoices):
        E = 'E', 'E-Rank'
        D = 'D', 'D-Rank'
        C = 'C', 'C-Rank'
        B = 'B', 'B-Rank'
        A = 'A', 'A-Rank'
        S = 'S', 'S-Rank'

    date_joined = models.DateField(auto_now_add=True)
    rank = models.CharField(max_length=1, choices=RankChoices.choices)
    guild = models.ForeignKey('Guild', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    skills = models.ManyToManyField('Skill', related_name='hunters', blank=True)
    completed_raids = models.ManyToManyField('Raid', through='RaidParticipation', related_name='completed_by')

    class Meta:
        verbose_name = "Hunter"
        verbose_name_plural = "Hunters"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def rank_display(self):
        return self.get_rank_display()
    
    @property
    def power_level(self):
        base_power = {'E': 10, 'D': 30, 'C': 50, 'B': 80, 'A': 120, 'S': 200}
        return base_power[self.rank] + sum(skill.power for skill in self.skills.all())

    def __str__(self):
        return f"{self.full_name} ({self.rank_display()})"

    
class Guild(models.Model):
    name = models.CharField(max_length=100)
    founded_date = models.DateField(auto_now_add=True)
    leader = models.OneToOneField('Hunter', on_delete=models.SET_NULL, null=True, blank=True, related_name='led_guild')

    @property
    def member_count(self):
        return self.members.count()

    def __str__(self):
        return self.name


class Skill(models.Model):
    class ElementChoices(models.TextChoices):
        Fire = 'Fire'
        Water = 'Water'
        Earth = 'Earth'
        Shadow = 'Shadow'
        Light = 'Light'

    name = models.CharField(max_length=100)
    element = models.CharField(max_length=10, choices=ElementChoices.choices)
    power = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.element})"


class Dungeon(models.Model):
    RANK_CHOICES = Hunter.RankChoices.choices

    name = models.CharField(max_length=100)
    rank = models.CharField(max_length=1, choices=RANK_CHOICES)
    location = models.CharField(max_length=200)
    is_open = models.BooleanField(default=True)

    @property
    def rank_display(self):
        return self.get_rank_display()

    def __str__(self):
        return f"{self.name} ({self.rank_display()})"


class Raid(models.Model):
    name = models.CharField(max_length=100)
    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE, related_name='raids')
    date = models.DateField()
    success = models.BooleanField(default=False)

    @property
    def team_strength(self):
        return sum(hunter.power_level for hunter in self.team.all())

    def __str__(self):
        return f"{self.name} - {self.dungeon.name}"


class RaidParticipation(models.Model):
    class RoleChoices(models.TextChoices):
        Tank = 'Tank'
        DPS = 'DPS'
        Healer = 'Healer'
        Support = 'Support'

    raid = models.ForeignKey(Raid, on_delete=models.CASCADE, related_name='participations')
    hunter = models.ForeignKey(Hunter, on_delete=models.CASCADE, related_name='participations')
    role = models.CharField(max_length=10, choices=RoleChoices.choices)

    def __str__(self):
        full_name = f"{self.hunter.first_name} {self.hunter.last_name}".strip()
        return f"{full_name} in {self.raid.name} as {self.role}"


