from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Language


class LanguageViewTests(APITestCase):
    def setUp(self):
        self.language = Language.objects.create(name="English")
        self.language_url = reverse('language-list-create')
        self.language_detail_url = reverse('language-detail', kwargs={'pk': self.language.pk})

    def test_create_language(self):
        data = {'name': 'French'}
        response = self.client.post(self.language_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Language.objects.count(), 2)
        self.assertEqual(Language.objects.get(id=response.data['id']).name, 'French')

    # def test_get_languages(self):
    #     response = self.client.get(self.language_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 1)

    # def test_get_language_detail(self):
    #     response = self.client.get(self.language_detail_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['languages'][0]['name'], self.language.name)

    def test_update_language(self):
        data = {'name': 'Spanish'}
        response = self.client.put(self.language_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.language.refresh_from_db()
        self.assertEqual(self.language.name, 'Spanish')

    def test_delete_language(self):
        response = self.client.delete(self.language_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Language.objects.count(), 0)
