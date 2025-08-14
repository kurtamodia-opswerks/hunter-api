from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random

from api.models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation

fake = Faker()

class Command(BaseCommand):
    help = "Populate the database with sample data"

    def handle(self, *args, **kwargs):
        # Clear old data
        RaidParticipation.objects.all().delete()
        Raid.objects.all().delete()
        Dungeon.objects.all().delete()
        Skill.objects.all().delete()
        Hunter.objects.all().delete()
        Guild.objects.all().delete()

        # Create Skills
        elements = ['Fire', 'Water', 'Earth', 'Wind', 'Light', 'Dark']
        skills = []
        for _ in range(10):
            skill = Skill.objects.create(
                name=fake.word().capitalize(),
                element=random.choice(elements),
                power=random.randint(10, 100)
            )
            skills.append(skill)
        self.stdout.write(self.style.SUCCESS("✅ Created Skills"))

        # Create Guilds
        guilds = []
        for _ in range(3):
            guild = Guild.objects.create(
                name=f"{fake.color_name()} Guild",
                leader=None,  # leader will be assigned later
                founded_date=fake.date_this_decade()
            )
            guilds.append(guild)
        self.stdout.write(self.style.SUCCESS("Created Guilds"))

        # Create Hunters
        ranks = ['S', 'A', 'B', 'C']
        hunters = []
        for _ in range(15):
            hunter = Hunter.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="password123",
                rank=random.choice(ranks),
                guild=random.choice(guilds)
            )
            hunter.skills.set(random.sample(skills, k=random.randint(1, 3)))
            hunters.append(hunter)
        self.stdout.write(self.style.SUCCESS("Created Hunters"))

        # Assign leaders to guilds
        for guild in guilds:
            leader = random.choice(hunters)
            guild.leader = leader
            guild.save()

        # Create Dungeons
        dungeons = []
        for _ in range(5):
            dungeon = Dungeon.objects.create(
                name=f"{fake.city()} Dungeon",
                rank=random.choice(ranks),
                location=fake.city(),
                is_open=random.choice([True, False])
            )
            dungeons.append(dungeon)
        self.stdout.write(self.style.SUCCESS("Created Dungeons"))

        # Create Raids
        raids = []
        for _ in range(8):
            raid = Raid.objects.create(
                name=f"{fake.word().capitalize()} Raid",
                dungeon=random.choice(dungeons),
                date=fake.date_this_year(),
                success=random.choice([True, False])
            )
            raids.append(raid)
        self.stdout.write(self.style.SUCCESS("Created Raids"))

        # Create Raid Participations
        roles = ['Tank', 'DPS', 'Healer']
        for raid in raids:
            participants = random.sample(hunters, k=random.randint(3, 6))
            for hunter in participants:
                RaidParticipation.objects.create(
                    hunter=hunter,
                    raid=raid,
                    role=random.choice(roles),
                    damage_dealt=random.randint(1000, 10000),
                    healing_done=random.randint(0, 5000)
                )
        self.stdout.write(self.style.SUCCESS("Created Raid Participations"))

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))
