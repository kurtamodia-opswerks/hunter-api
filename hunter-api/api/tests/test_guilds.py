from api.models import Guild
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class GuildTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="test", email="admin@example.com", rank="S"
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_guild(self):
        url = reverse("guild-list")
        data = {"name": "Frost Wolves", "leader": self.admin.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
