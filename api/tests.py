from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Hunter, Guild, Skill, Dungeon, Raid, RaidParticipation
from django.utils import timezone

class HunterAPITestCase(APITestCase):
    def setUp(self):
        self.guild = Guild.objects.create(name='Test Guild', leader=None)
        self.skill = Skill.objects.create(name='Fireball', element='Fire', power=50)

        # Create Admin Hunter
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

        # Create Normal Hunter
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

        # Create Hunter
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

class GuildAPITestCase(APITestCase):
    def setUp(self):
        # Create Guilds
        self.guild1 = Guild.objects.create(name='Guild One', leader=None)
        self.guild2 = Guild.objects.create(name='Guild Two', leader=None)

        # Create Hunters
        self.admin_hunter = Hunter.objects.create(
            username='adminhunter',
            first_name='Admin',
            last_name='Hunter',
            email='admin@example.com',
            rank='A',
            guild=self.guild1,
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
            guild=self.guild2,
            is_staff=False,
            is_superuser=False
        )
        self.normal_hunter.set_password('userpass')
        self.normal_hunter.save()

        # URLs
        self.list_url = reverse('guild-list')
        self.detail_url = reverse('guild-detail', kwargs={'pk': self.guild1.pk})

    def test_get_guild_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        guild_names = [g['name'] for g in response.data['results']]
        self.assertIn(self.guild1.name, guild_names)
        self.assertIn(self.guild2.name, guild_names)

    def test_get_guild_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.guild1.id)

    def test_create_guild_unauthorized(self):
        data = {'name': 'New Guild'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_guild_as_admin(self):
        self.client.login(username='adminhunter', password='adminpass')
        
        data = {
            'name': 'Admin Guild',
            'leader': self.admin_hunter.pk  
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Guild.objects.filter(name='Admin Guild').exists())

    def test_update_guild_as_admin(self):
        self.client.login(username='adminhunter', password='adminpass')
        data = {'name': 'Updated Guild'}
        response = self.client.patch(self.detail_url, data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        self.guild1.refresh_from_db()
        self.assertEqual(self.guild1.name, 'Updated Guild')

    def test_delete_guild_permissions(self):
        # Normal hunter should not delete
        self.client.login(username='normalhunter', password='userpass')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Guild.objects.filter(pk=self.guild1.pk).exists())

        # Admin hunter can delete
        self.client.login(username='adminhunter', password='adminpass')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Guild.objects.filter(pk=self.guild1.pk).exists())


class RaidAPITestCase(APITestCase):
    def setUp(self):
        self.guild = Guild.objects.create(name='Test Guild', leader=None)
        self.dungeon = Dungeon.objects.create(
            name='Ancient Crypt',
            location='North',
            rank='A',
            is_open=True
        )

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

        self.hunter1 = Hunter.objects.create(
            username='hunter1',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            rank='B',
            guild=self.guild
        )
        self.hunter1.set_password('hunterpass1')
        self.hunter1.save()

        self.hunter2 = Hunter.objects.create(
            username='hunter2',
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            rank='C',
            guild=self.guild
        )
        self.hunter2.set_password('hunterpass2')
        self.hunter2.save()

        self.raid = Raid.objects.create(
            name='Crypt Raid',
            dungeon=self.dungeon,
            date=timezone.now(),
            success=True
        )
        RaidParticipation.objects.create(
            raid=self.raid,
            hunter=self.hunter1,
            role=RaidParticipation.RoleChoices.DPS,
            damage_dealt=1000
        )

        self.list_url = reverse('raid-list')
        self.detail_url = reverse('raid-detail', kwargs={'pk': self.raid.raid_id})  # UUID PK

    def test_get_raid_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        raid_names = [r['name'] for r in response.data['results']]
        self.assertIn('Crypt Raid', raid_names)

    def test_get_raid_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['raid_id'], str(self.raid.raid_id))  # UUID check
        self.assertIn('participations', response.data)

    def test_create_raid_as_admin(self):
        self.client.login(username='adminhunter', password='adminpass')
        data = {
            'name': 'New Raid',
            'dungeon': self.dungeon.id,
            'date': "2025-08-15",
            'success': False,
            'participations': [
                {'hunter_id': self.hunter1.id, 'role': 'DPS'},
                {'hunter_id': self.hunter2.id, 'role': 'Healer'}
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        raid = Raid.objects.get(name='New Raid')
        self.assertEqual(raid.participations.count(), 2)

    def test_create_raid_invalid_hunter(self):
        self.client.login(username='adminhunter', password='adminpass')
        data = {
            'name': 'Invalid Raid',
            'dungeon': self.dungeon.id,
            'date': "2025-08-15",
            'success': True,
            'participations': [{'hunter_id': 9999, 'role': 'DPS'}]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Hunter does not exist', str(response.data))

    def test_delete_raid_permissions(self):
        self.client.login(username='hunter1', password='hunterpass1')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username='adminhunter', password='adminpass')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
