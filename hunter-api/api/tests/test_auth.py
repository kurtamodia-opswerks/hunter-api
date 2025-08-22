from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", password="test", email="admin@example.com", rank="S"
        )

    def test_token_obtain_and_refresh(self):
        url = reverse("token_obtain_pair")  # adjust to your actual URL name
        response = self.client.post(
            url, {"username": "admin", "password": "test"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
