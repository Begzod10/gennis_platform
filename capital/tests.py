from django.test import TestCase
from rest_framework.test import APIClient
from .models import Capital, CapitalCategory
from django.urls import reverse
from rest_framework import status
from branch.models import Branch
from payments.models import PaymentTypes


class CapitalModelTest(TestCase):
    def setUp(self):
        self.payment_type = PaymentTypes.objects.create(name='Credit Card')
        self.branch = Branch.objects.create(name='Main Branch', number=1)
        self.category = CapitalCategory.objects.create(
            name="Test ClassTypes",
            id_number="1",
        )
        self.capital = Capital.objects.create(
            name="Test Capital",
            id_number='svsdv',
            price=1423,
            total_down_cost=55443,
            curriculum_hours=234234,
            term='2024-05-06',
            branch=self.branch,
            payment_type=self.payment_type,
            category=self.category,
        )

    def test_class_coin_creation(self):
        self.assertEqual(self.capital.value, "Test Capital")


class CapitalAPITestCase(TestCase):
    def setUp(self):
        self.payment_type = PaymentTypes.objects.create(name='Credit Card')
        self.branch = Branch.objects.create(name='Main Branch', number=1)
        self.category = CapitalCategory.objects.create(
            name="Test ClassTypes",
            id_number="1",
        )
        self.capital = Capital.objects.create(
            name="Test Capital",
            id_number='svsdv',
            price=1423,
            total_down_cost=55443,
            curriculum_hours=234234,
            term='2024-05-06',
            branch=self.branch,
            payment_type=self.payment_type,
            category=self.category,
        )

    def test_create_capital(self):
        url = reverse('capital-create')
        data = {
            'value': 'New Capital',
            'id_number': '12',
            'price': 5343,
            'total_down_cost': 54654,
            'curriculum_hours': 12435343,
            'term': '2024-05-06',
            'branch': self.branch,
            'payment_type': self.payment_type,
            'category': self.category,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Capital.objects.count(), 2)

    def test_retrieve_capital(self):
        url = reverse('capital', args=[self.capital.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'Test Capital')

    def test_update_capital(self):
        url = reverse('capital-update', args=[self.capital.id])
        data = {'value': 'Capital'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'Capital')

    def test_delete_capital(self):
        url = reverse('capital-delete', args=[self.capital.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CapitalCategoryModelTest(TestCase):
    def setUp(self):
        self.class_types = CapitalCategory.objects.create(
            name="Test CapitalCategory",
            id_number="1",
        )

    def test_lead_creation(self):
        self.assertEqual(self.class_types.name, "Test CapitalCategory")


class CapitalCategoryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.capital_category = CapitalCategory.objects.create(
            name="Test CapitalCategory",
            id_number="1",
        )

    def test_create_capital_category(self):
        url = reverse('capital-category-list-create')
        data = {
            'name': 'New CapitalCategory',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CapitalCategory.objects.count(), 2)

    def test_retrieve_capital_category(self):
        url = reverse('capital-category-detail', args=[self.capital_category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test CapitalCategory')

    def test_update_capital_category(self):
        url = reverse('capital-category-detail', args=[self.capital_category.id])
        data = {'name': 'Test CapitalCategory2'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test CapitalCategory2')

    def test_delete_capital_category(self):
        url = reverse('capital-category-detail', args=[self.capital_category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CapitalCategory.objects.count(), 0)
