from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from .models import System


class SystemAPITestCase(APITestCase):
    def setUp(self):
        self.system = System.objects.create(name="Test System", number=123)
        self.create_url = reverse('system-list-create')

    def test_create_system(self):

        data = {'name': 'New System', 'number': 456}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(System.objects.count(), 2)
        self.assertEqual(System.objects.get(id=response.data['id']).name, 'New System')

    def test_list_systems(self):
        response = self.client.get(self.create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], self.system.name)

    def test_retrieve_system(self):
        url = reverse('system-detail', kwargs={'pk': self.system.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.system.name)

    def test_update_system(self):
        url = reverse('system-detail', kwargs={'pk': self.system.id})
        data = {'name': 'Updated System', 'number': 789}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(System.objects.get(id=self.system.id).name, 'Updated System')

    def test_delete_system(self):
        url = reverse('system-detail', kwargs={'pk': self.system.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(System.objects.count(), 0)
