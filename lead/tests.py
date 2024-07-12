from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Lead, LeadCall, Subject, Branch
from django.contrib.auth.models import User

class LeadModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Math", ball_number=10)
        self.branch = Branch.objects.create(name="Main Branch", number=1)

        self.lead = Lead.objects.create(
            name="John Doe",
            phone="1234567890",
            subject=self.subject,
            branch=self.branch
        )

    def test_lead_creation(self):
        self.assertEqual(self.lead.name, "John Doe")
        self.assertEqual(self.lead.phone, "1234567890")
        self.assertEqual(self.lead.subject, self.subject)
        self.assertEqual(self.lead.branch, self.branch)

class LeadCallModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Math", ball_number=10)
        self.branch = Branch.objects.create(name="Main Branch", number=1)
        self.lead = Lead.objects.create(
            name="John Doe",
            phone="1234567890",
            subject=self.subject,
            branch=self.branch
        )
        self.lead_call = LeadCall.objects.create(
            lead=self.lead,
            delay="2024-07-12",
            comment="Test call"
        )

    def test_lead_call_creation(self):
        self.assertEqual(self.lead_call.lead, self.lead)
        self.assertEqual(self.lead_call.delay, "2024-07-12")
        self.assertEqual(self.lead_call.comment, "Test call")

class LeadAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject = Subject.objects.create(name="Math", ball_number=10)
        self.branch = Branch.objects.create(name="Main Branch", number=1)
        self.lead = Lead.objects.create(
            name="John Doe",
            phone="1234567890",
            subject=self.subject,
            branch=self.branch
        )

    def test_create_lead(self):
        url = reverse('lead-list-create')
        data = {
            'name': 'Jane Doe',
            'phone': '0987654321',
            'subject': self.subject.id,
            'branch': self.branch.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lead.objects.count(), 2)

    def test_retrieve_lead(self):
        url = reverse('lead-detail', args=[self.lead.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')

    def test_update_lead(self):
        url = reverse('lead-detail', args=[self.lead.id])
        data = {'name': 'John Smith'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Smith')

    def test_delete_lead(self):
        url = reverse('lead-detail', args=[self.lead.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lead.objects.count(), 0)

class LeadCallAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject = Subject.objects.create(name="Math", ball_number=10)
        self.branch = Branch.objects.create(name="Main Branch", number=1)
        self.lead = Lead.objects.create(
            name="John Doe",
            phone="1234567890",
            subject=self.subject,
            branch=self.branch
        )
        self.lead_call = LeadCall.objects.create(
            lead=self.lead,
            delay="2024-07-12",
            comment="Test call"
        )

    def test_create_lead_call(self):
        url = reverse('lead-call-list-create')
        data = {
            'lead': self.lead.id,
            'delay': "2024-07-15",
            'comment': "New test call"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeadCall.objects.count(), 2)

    def test_retrieve_lead_call(self):
        url = reverse('lead-call-detail', args=[self.lead_call.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], "Test call")

    def test_update_lead_call(self):
        url = reverse('lead-call-detail', args=[self.lead_call.id])
        data = {'comment': 'Updated test call'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Updated test call')

    def test_delete_lead_call(self):
        url = reverse('lead-call-detail', args=[self.lead_call.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LeadCall.objects.count(), 0)
