from django.test import TestCase, Client
from django.urls import reverse
from Calendar.models import TypeDay  # Import your model if not already imported in views


class TypeDayViewsTestCase(TestCase):

    def setUp(self):
        # Create sample data for testing
        self.type_day = TypeDay.objects.create(
            type='Test Type Day',
            color='Description of Test Type Day'
        )
        self.client = Client()

    def test_type_day_list_view(self):
        url = reverse('type_day-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Add more assertions as needed to validate the response

    def test_type_day_create_view(self):
        url = reverse('type_day-create')
        data = {
            'type': 'New Type Day',
            'color': 'Description of New Type Day'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)  # Assuming it returns HTTP 201 for successful creation
        # Add assertions to verify the creation logic

    def test_type_day_delete_view(self):
        url = reverse('type_day-delete', args=[self.type_day.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)  # Assuming it returns HTTP 204 for successful deletion
        # Verify that the object is deleted from the database

    def test_type_day_update_view(self):
        url = reverse('type_day-update', args=[self.type_day.pk])
        data = {
            'type': 'Updated Type Day',
            'color': 'Updated Description'
        }
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Assuming it returns HTTP 200 for successful update
        # Verify that the object is updated correctly

    def test_type_day_detail_view(self):
        url = reverse('type_day-retrieve', args=[self.type_day.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Add assertions to verify the details retrieved


class CalendarViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_calendar_view(self):
        url = reverse('get-calendar', args=[2023, 2024])  # Adjust years as needed
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Add assertions to validate calendar data retrieval



