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


