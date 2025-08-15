from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation


class HunterAPITestCase(APITestCase):
    def setUp(self):
        self.guild = Guild.objects.create(name='Test Guild', leader=None)
        self.skill = Skill.objects.create(name='Fireball', element='Fire', power=50)

        self.admin_hunter = Hunter.objects.create(
            username='adminhunter',
            first_name='Admin',
            last_name='Hunter',
            email='admin@example.com',
            rank='A',
            guild=self.guild,
            is_staff=True,
            is_superuser=True
        )
        self.admin_hunter.set_password('adminpass')
        self.admin_hunter.save()

        self.normal_hunter = Hunter.objects.create(
            username='normalhunter',
            first_name='Normal',
            last_name='Hunter',
            email='normal@example.com',
            rank='C',
            guild=self.guild,
            is_staff=False,
            is_superuser=False
        )
        self.normal_hunter.set_password('userpass')
        self.normal_hunter.save()

        self.hunter = Hunter.objects.create(
            username='johndoe',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            rank='C',
            guild=self.guild
        )
        self.hunter.skills.add(self.skill)
        self.hunter.set_password('hunterpass')
        self.hunter.save()

        self.detail_url = reverse('hunter-detail', kwargs={'pk': self.hunter.pk})
        self.list_url = reverse('hunter-list')

    def test_get_hunter_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        hunter_ids = [h['id'] for h in response.data['results']]
        self.assertIn(self.hunter.id, hunter_ids)


    def test_get_hunter_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.hunter.id)

    def test_create_hunter_unauthorized(self):
        data = {
            'first_name': 'Alice',
            'last_name': 'Smith',
            'username': 'alicesmith',
            'password': 'password123',
            'email': 'alice@example.com',
            'rank': 'B'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_hunter_as_admin(self):
        self.client.login(username='adminhunter', password='adminpass')
        data = {
            'first_name': 'Alice',
            'last_name': 'Smith',
            'username': 'alicesmith',
            'password': 'password123',
            'email': 'alice@example.com',
            'rank': 'B'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Hunter.objects.filter(username='alicesmith').exists())

    def test_update_hunter_as_admin(self):
        self.client.login(username='adminhunter', password='adminpass')
        data = {'first_name': 'Johnny'}
        response = self.client.put(self.detail_url, data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_delete_hunter_permissions(self):
        self.client.login(username='normalhunter', password='userpass')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Hunter.objects.filter(pk=self.hunter.pk).exists())

        self.client.login(username='adminhunter', password='adminpass')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Hunter.objects.filter(pk=self.hunter.pk).exists())
