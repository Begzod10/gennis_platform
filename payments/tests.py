from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import PaymentTypes


class PaymentTypesTests(APITestCase):
    def setUp(self):
        self.payment_type1 = PaymentTypes.objects.create(name='Credit Card')
        self.payment_type2 = PaymentTypes.objects.create(name='PayPal')
        self.list_url = reverse('payment_type-list-create')
        self.detail_url = reverse('payment_type-detail', args=[self.payment_type1.pk])

    def test_list_payment_types(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_payment_type(self):
        data = {'name': 'Bank Transfer'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentTypes.objects.count(), 3)
        self.assertEqual(PaymentTypes.objects.latest('id').name, 'Bank Transfer')

    def test_retrieve_payment_type(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.payment_type1.name)

    def test_update_payment_type(self):
        data = {'name': 'Debit Card'}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment_type1.refresh_from_db()
        self.assertEqual(self.payment_type1.name, 'Debit Card')

