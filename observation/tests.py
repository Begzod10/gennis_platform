from django.test import TestCase
from rest_framework.test import APIClient
from .models import ObservationInfo, ObservationOptions, ObservationDay, ObservationStatistics
from django.urls import reverse
from rest_framework import status
from branch.models import Branch
from payments.models import PaymentTypes


class ObservationOptionsModelTest(TestCase):
    def setUp(self):
        self.observation_options = ObservationOptions.objects.create(
            name="Test ObservationOptions",
            value=1,
        )

    def test_observation_options_creation(self):
        self.assertEqual(self.observation_options.title, "Test ObservationOptions")


class ObservationOptionsAPITestCase(TestCase):
    def setUp(self):
        self.observation_options = ObservationOptions.objects.create(
            name="Test ObservationOptions",
            value=1,
        )

    def test_retrieve_observation_options(self):
        url = reverse('observation-options-detail', args=[self.observation_options.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test ObservationOptions')
        self.assertEqual(response.data['value'], 1)

    def test_update_observation_options(self):
        url = reverse('observation-options-detail', args=[self.observation_options.id])
        data = {'title': 'ObservationOptions'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'ObservationInfo')


class ObservationInfoModelTest(TestCase):
    def setUp(self):
        self.observation_info = ObservationInfo.objects.create(
            title="Test ObservationInfo",
        )

    def test_observation_info_creation(self):
        self.assertEqual(self.observation_info.title, "Test ObservationInfo")


class ObservationInfoAPITestCase(TestCase):
    def setUp(self):
        self.observation_info = ObservationInfo.objects.create(
            title="Test ObservationInfo",
        )

    def test_retrieve_observation_info(self):
        url = reverse('observation-info-detail', args=[self.observation_info.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'Test ObservationInfo')

    def test_update_observation_info(self):
        url = reverse('observation-info-detail', args=[self.observation_info.id])
        data = {'title': 'ObservationInfo'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'ObservationInfo')


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
