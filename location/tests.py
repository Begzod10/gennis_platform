from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Location
from system.models import System


class LocationAPITestCase(APITestCase):

    def setUp(self):
        self.system = System.objects.create(name='Test System',number=1)
        self.location = Location.objects.create(
            name='Test Location',
            number=1,
            system=self.system
        )
        self.list_url = reverse('location-list-create')
        self.detail_url = reverse('location-detail', kwargs={'pk': self.location.pk})

    def test_create_location(self):
        data = {
            'name': 'New Location',
            'number': 2,
            'system': self.system.pk
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.count(), 2)
        self.assertEqual(Location.objects.get(pk=response.data['id']).name, 'New Location')

    def test_list_locations(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_location(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.location.name)

    def test_update_location(self):
        data = {
            'name': 'Updated Location',
            'number': 3,
            'system': self.system.pk
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, 'Updated Location')

    def test_delete_location(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Location.objects.count(), 0)
