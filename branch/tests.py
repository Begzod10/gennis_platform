from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from location.models import Location
from system.models import System
from .models import Branch


class BranchTests(APITestCase):

    def setUp(self):
        self.system = System.objects.create(number=1, name='Test System')
        self.location = Location.objects.create(name='Test Location', number=1, system=self.system)
        self.branch_data = {
            'name': 'Test Branch',
            'number': 1,
            'location': self.location.id
        }
        self.branch = Branch.objects.create(
            name='Existing Branch',
            number=2,
            location=self.location
        )
        self.create_url = reverse('branch-list-create')

    def test_create_branch(self):
        response = self.client.post(self.create_url, self.branch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Branch.objects.count(), 2)
        self.assertEqual(Branch.objects.get(id=response.data['id']).name, self.branch_data['name'])

    def test_list_branches(self):
        response = self.client.get(self.create_url, format='json')
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_branch(self):
        url = reverse('branch-detail', kwargs={'pk': self.branch.id})
        response = self.client.get(url, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.branch.name)

    def test_update_branch(self):
        url = reverse('branch-detail', kwargs={'pk': self.branch.id})
        updated_data = {
            'name': 'Updated Branch',
            'number': 3,
            'location': self.location.id
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.branch.refresh_from_db()
        self.assertEqual(self.branch.name, updated_data['name'])

    def test_delete_branch(self):
        url = reverse('branch-detail', kwargs={'pk': self.branch.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Branch.objects.count(), 0)
