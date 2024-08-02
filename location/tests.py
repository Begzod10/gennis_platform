from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Location
from system.models import System


class LocationAPITestCase(APITestCase):

    def setUp(self):
        self.system = System.objects.create(name='Test System', number=1)
        self.location = Location.objects.create(
            name='Test Location',
            number=1,
            system=self.system
        )
        self.list_url = reverse('location-list')
        self.create_url = reverse('location-create')
        self.delete_url = reverse('location-delete', kwargs={'pk': self.location.pk})
        self.update_url = reverse('location-update', kwargs={'pk': self.location.pk})
        self.get_url = reverse('location', kwargs={'pk': self.location.pk})

    def test_create_location(self):
        location_data = {
            'name': 'New Location',
            'number': 2,
            'system': {
                'name': self.system.name,
                'number': self.system.number
            }
        }
        response = self.client.post(self.create_url, location_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_locations(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_location(self):
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.location.name)

    def test_update_location(self):
        data = {
            'name': 'Updated Location',
            'number': 2,
            'system': {
                'name': self.system.name,
                'number': self.system.number
            }
        }
        response = self.client.put(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, 'Updated Location')

    def test_delete_location(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Location.objects.count(), 0)
