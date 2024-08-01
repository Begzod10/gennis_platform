from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from branch.models import Branch
from .models import Overhead, PaymentTypes


class OverheadAPITest(APITestCase):
    def setUp(self):
        self.payment_type = PaymentTypes.objects.create(name='Credit Card')
        self.branch = Branch.objects.create(id=2, name='Main Branch',number=1)  # Ensure this branch exists
        self.overhead = Overhead.objects.create(name='Office Supplies', payment=self.payment_type, price=5000,
                                                branch=self.branch)
        self.list_url = reverse('overhead-create')
        self.detail_url = reverse('overhead-update', kwargs={'pk': self.overhead.pk})

        self.valid_payload = {
            'name': 'Office Rent',
            'created': '2024-07-18T10:00:00Z',
            'payment': self.payment_type.id,
            'price': 15000,
            'branch': self.branch.id
        }
        self.invalid_payload = {
            'name': '',
            'created': '2024-07-18T10:00:00Z',
            'payment': self.payment_type.id,
            'price': 15000,
            'branch': self.branch.id
        }

    def test_create_overhead(self):
        response = self.client.post(self.list_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.valid_payload['name'])

    def test_update_overhead(self):
        update_payload = {
            'name': 'Office Rent Updated',
            'created': '2024-07-18T10:00:00Z',
            'payment': self.payment_type.id,
            'price': 20000,
            'branch': 2
        }
        response = self.client.patch(self.detail_url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], update_payload['name'])
