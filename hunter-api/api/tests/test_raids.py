from datetime import date

from api.models import Dungeon, Raid
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RaidTests(APITestCase):
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
        self.client.force_authenticate(user=self.admin)

    def test_create_raid_with_participations(self):
        url = reverse("raid-list")
        data = {
            "name": "Dragon Hunt",
            "dungeon": self.dungeon.id,
            "date": date.today(),
            "success": False,
            "participations_create": [
                {"hunter_id": self.admin.id, "role": "Tank"},
                {"hunter_id": self.user.id, "role": "DPS"},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
