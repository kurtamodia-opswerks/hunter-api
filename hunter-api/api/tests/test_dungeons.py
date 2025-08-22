from api.models import Dungeon
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class DungeonTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="test", email="admin@example.com", rank="S"
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_dungeon(self):
        url = reverse("dungeon-list")
        data = {
            "name": "Ice Cave",
            "location": "North Mountains",
            "rank": "A",
            "is_open": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
