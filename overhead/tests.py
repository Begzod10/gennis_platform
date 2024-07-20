from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Overhead, PaymentTypes

class OverheadAPITest(APITestCase):
    def setUp(self):
        self.payment_type = PaymentTypes.objects.create(name='Credit Card')
        self.overhead = Overhead.objects.create(name='Office Supplies', payment=self.payment_type, price=5000)
        self.overhead_list_create_url = reverse('overhead-list-create')
        self.overhead_detail_url = reverse('overhead-detail', kwargs={'pk': self.overhead.pk})
        self.valid_payload = {
            'name': 'Office Rent',
            'created': '2024-07-18T10:00:00Z',
            'payment': {'name': 'Credit Card'},
            'price': 15000
        }
        self.invalid_payload = {
            'name': '',
            'created': '2024-07-18T10:00:00Z',
            'payment': {'name': 'Credit Card'},
            'price': 15000
        }

    def test_create_overhead(self):
        response = self.client.post(self.overhead_list_create_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.valid_payload['name'])

    def test_create_overhead_invalid(self):
        response = self.client.post(self.overhead_list_create_url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_overhead(self):
        response = self.client.get(self.overhead_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.overhead.name)

    def test_update_overhead(self):
        update_payload = {
            'name': 'Office Rent Updated',
            'created': '2024-07-18T10:00:00Z',
            'payment': {'name': 'Credit Card'},
            'price': 20000
        }
        response = self.client.put(self.overhead_detail_url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], update_payload['name'])

    def test_delete_overhead(self):
        response = self.client.delete(self.overhead_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Overhead.objects.filter(pk=self.overhead.pk).exists())
