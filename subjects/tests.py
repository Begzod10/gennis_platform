from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Subject, SubjectLevel


class SubjectModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(
            name="Test Subject",
            ball_number="1234567890",
        )

    def test_subject_creation(self):
        self.assertEqual(self.subject.name, "Test Subject")
        self.assertEqual(self.subject.ball_number, "1234567890")


class SubjectLevelModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(
            name="Test Subject",
            ball_number="1234567890",
        )
        self.subject_level = SubjectLevel.objects.create(
            subject=self.subject,
            name="Test SubjectLevel",
        )

    def test_subject_level_creation(self):
        self.assertEqual(self.subject_level.subject, self.subject)
        self.assertEqual(self.subject_level.name, "Test SubjectLevel")


class SubjectAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.subject = Subject.objects.create(
            name="Test Subject",
            ball_number="1234567890",
        )

    def test_retrieve_subject(self):
        url = reverse('subject-retrieve', args=[self.subject.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Subject')


class SubjectLevelAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject = Subject.objects.create(
            name="Test Subject",
            ball_number="1234567890",
        )
        self.subject_level = SubjectLevel.objects.create(
            subject=self.subject,
            name="Test SubjectLevel",
        )

    def test_retrieve_subject_level(self):
        url = reverse('subject-level-retrieve', args=[self.subject_level.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test SubjectLevel")
