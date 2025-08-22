import random
from datetime import date, timedelta

from api.models import Dungeon, Guild, Raid, RaidParticipation, Skill
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

Hunter = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with demo data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old data...")
        RaidParticipation.objects.all().delete()
        Raid.objects.all().delete()
        Dungeon.objects.all().delete()
        Guild.objects.all().delete()
        Skill.objects.all().delete()
        Hunter.objects.all().delete()

        self.stdout.write("Creating skills...")
        skills = [
            Skill.objects.create(name="Fireball", element="Fire", power=50),
            Skill.objects.create(name="Ice Blast", element="Water", power=40),
            Skill.objects.create(name="Earthquake", element="Earth", power=70),
            Skill.objects.create(name="Shadow Strike", element="Shadow", power=60),
            Skill.objects.create(name="Holy Light", element="Light", power=80),
        ]

        self.stdout.write("Creating hunters (users)...")
        admin = Hunter.objects.create_superuser(
            username="admin", email="admin@example.com", password="test", rank="S"
        )

        hunters = [
            Hunter.objects.create_user(
                username="jinwoo",
                first_name="Jin",
                last_name="Woo",
                email="jinwoo@example.com",
                password="test",
                rank="E",
            ),
            Hunter.objects.create_user(
                username="david",
                first_name="David",
                last_name="Porras",
                email="david@example.com",
                password="test",
                rank="D",
            ),
            Hunter.objects.create_user(
                username="cj",
                first_name="CJ",
                last_name="Pingal",
                email="cj@example.com",
                password="test",
                rank="C",
            ),
            Hunter.objects.create_user(
                username="sung",
                first_name="Sung",
                last_name="Jin",
                email="sung@example.com",
                password="test",
                rank="B",
            ),
        ]

        # Assign random skills
        for h in hunters:
            h.skills.add(random.choice(skills))

        self.stdout.write("Creating guilds...")
        guild1 = Guild.objects.create(name="Hunters Guild", leader=hunters[0])
        guild2 = Guild.objects.create(name="Shadow Wolves", leader=hunters[1])

        hunters[0].guild = guild1
        hunters[0].save()
        hunters[1].guild = guild2
        hunters[1].save()

        self.stdout.write("Creating dungeons...")
        dungeon1 = Dungeon.objects.create(
            name="Goblin Cave", location="Seoul", rank="E", is_open=True
        )
        dungeon2 = Dungeon.objects.create(
            name="Orc Fortress", location="Busan", rank="C", is_open=True
        )
        dungeon3 = Dungeon.objects.create(
            name="Dragon Lair", location="Jeju", rank="S", is_open=False
        )

        self.stdout.write("Creating raids...")
        raid1 = Raid.objects.create(
            name="Goblin Hunt",
            dungeon=dungeon1,
            date=date.today(),
            success=True,
        )
        raid2 = Raid.objects.create(
            name="Dragon Hunt",
            dungeon=dungeon3,
            date=date.today() - timedelta(days=7),
            success=False,
        )

        RaidParticipation.objects.create(raid=raid1, hunter=hunters[0], role="Tank")
        RaidParticipation.objects.create(raid=raid1, hunter=hunters[1], role="DPS")
        RaidParticipation.objects.create(raid=raid2, hunter=hunters[2], role="Healer")

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))
