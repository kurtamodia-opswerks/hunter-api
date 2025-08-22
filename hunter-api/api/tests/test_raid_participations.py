from api.models import Dungeon, Raid, RaidParticipation
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class RaidParticipationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="test", email="admin@example.com", rank="S"
        )
        self.user = User.objects.create_user(
            username="user1", password="test", email="user1@example.com", rank="D"
        )
        self.dungeon = Dungeon.objects.create(
            name="Ant Cave", location="Jeju Island", rank="S"
        )
        self.raid = Raid.objects.create(
            name="Vampire Hunt", dungeon=self.dungeon, date="2025-08-21"
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_raid_participation(self):
        participation = RaidParticipation.objects.create(
            raid=self.raid, hunter=self.user, role="Healer"
        )
        self.assertEqual(participation.role, "Healer")
        self.assertEqual(participation.hunter, self.user)
        self.assertEqual(participation.raid, self.raid)
