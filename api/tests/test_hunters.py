from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Guild, Skill, Hunter

User = get_user_model()


class HunterAPITests(APITestCase):
    def setUp(self):
        # Create a guild and skill for relations
        self.guild = Guild.objects.create(name="Phantom Troupe")
        self.skill = Skill.objects.create(name="Shadow Slash", power=50)

        # Create regular hunter
        self.hunter = Hunter.objects.create_user(
            username="sjinwoo",
            password="test",
            first_name="Jin",
            last_name="Woo",
            email="jinwoo@example.com",
            rank="E"
        )

        # Create admin hunter
        self.admin = Hunter.objects.create_superuser(
            username="adminuser",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            rank="S"
        )

        # Auth tokens
        token_url = reverse("token_obtain_pair")
        self.hunter_token = self.client.post(token_url, {
            "username": "sjinwoo", "password": "test"
        }).data["access"]

        self.admin_token = self.client.post(token_url, {
            "username": "adminuser", "password": "adminpass"
        }).data["access"]

    def test_list_hunters(self):
        url = reverse("hunter-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data["results"]), 1)

    def test_retrieve_hunter(self):
        url = reverse("hunter-detail", args=[self.hunter.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "sjinwoo")

    def test_create_hunter_requires_admin(self):
        url = reverse("hunter-list")
        data = {
            "first_name": "David",
            "last_name": "Porras",
            "username": "davidporras",
            "password": "test",
            "email": "davidporras@example.com",
            "rank": "E",
            "skills": [self.skill.id],
            "guild": self.guild.id
        }

        # Non-admin cannot create
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.hunter_token}")
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin can create
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["username"], "davidporras")

    def test_update_hunter_requires_admin(self):
        url = reverse("hunter-detail", args=[self.hunter.id])
        data = {"rank": "D"}

        # Regular hunter cannot update
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.hunter_token}")
        res = self.client.put(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin can update
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        data = {
            "first_name": "Jin",
            "last_name": "Woo",
            "username": "sjinwoo",
            "password": "test",
            "email": "jinwoo@example.com",
            "rank": "D",
            "skills": [],
            "guild": None
        }
        res = self.client.put(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["rank"], "D")

    def test_patch_hunter_skills(self):
        url = reverse("hunter-detail", args=[self.hunter.id])
        data = {"skills": [self.skill.id]}

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        res = self.client.patch(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.skill.id, res.data["skills"])

    def test_delete_hunter_requires_admin(self):
        url = reverse("hunter-detail", args=[self.hunter.id])

        # Regular user cannot delete
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.hunter_token}")
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin can delete
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Hunter.objects.filter(id=self.hunter.id).exists())

    def test_invalid_rank_validation(self):
        url = reverse("hunter-list")
        data = {
            "first_name": "Invalid",
            "last_name": "Rank",
            "username": "invalidrank",
            "password": "test",
            "email": "invalid@example.com",
            "rank": "Z",  # invalid
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rank", res.data)
