from api.models import Skill
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class SkillTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="test", email="admin@example.com", rank="S"
        )
        self.client.force_authenticate(user=self.admin)
        self.skill = Skill.objects.create(
            name="Sword Dance", element="Light", power=120
        )

    def test_list_skills(self):
        url = reverse("skill-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_skill(self):
        url = reverse("skill-list")
        data = {"name": "Fire Blast", "element": "Fire", "power": 100}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_skill(self):
        url = reverse("skill-detail", args=[self.skill.id])
        data = {"name": "Sword Dance Plus", "element": "Light", "power": 150}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.power, 150)

    def test_delete_skill(self):
        url = reverse("skill-detail", args=[self.skill.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
