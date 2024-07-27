from django.test import TestCase
from rest_framework.test import APIClient
from .models import ObservationInfo, ObservationOptions, ObservationDay, ObservationStatistics
from django.urls import reverse
from rest_framework import status
from branch.models import Branch
from language.models import Language
from user.models import CustomUser
from subjects.models import Subject
from teachers.models import Teacher
from group.models import Group


class ObservationStatisticsModelTest(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Test Branch", number=1)
        self.language = Language.objects.create(name="English")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.teacher = Teacher.objects.create(
            user=self.user,
            subject=self.subject,
            color='blue',
            total_students=10
        )
        self.group = Group.objects.create(
            name='Test group',
            branch=self.branch,
        )
        self.observation_day = ObservationDay.objects.create(
            day="2022-04-07",
            average=212,
            comment='ObservationDay',
            user=self.user,
            group=self.group,
            teacher=self.teacher,
        )
        self.observation_options = ObservationOptions.objects.create(
            name="Test ObservationOptions",
            value=1,
        )
        self.observation_info = ObservationInfo.objects.create(
            title="Test ObservationInfo",
        )
        self.observation_statistics = ObservationStatistics.objects.create(
            comment='ObservationStatistics',
            observation_day=self.observation_day,
            observation_options=self.observation_options,
            observation_info=self.observation_info,

        )

    def test_observation_statistics_creation(self):
        self.assertEqual(self.observation_statistics.comment, "ObservationStatistics")


class ObservationStatisticsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.branch = Branch.objects.create(name="Test Branch", number=1)
        self.language = Language.objects.create(name="English")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.client.login(username="testuser", password="testpassword")
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.teacher = Teacher.objects.create(
            user=self.user,
            subject=self.subject,
            color='blue',
            total_students=10
        )
        self.group = Group.objects.create(
            name='Test group',
            branch=self.branch,
        )
        self.observation_day = ObservationDay.objects.create(
            day="2022-04-07",
            average=212,
            comment='ObservationDay',
            user=self.user,
            group=self.group,
            teacher=self.teacher,
        )
        self.observation_options = ObservationOptions.objects.create(
            name="Test ObservationOptions",
            value=1,
        )
        self.observation_info = ObservationInfo.objects.create(
            title="Test ObservationInfo",
        )
        self.observation_statistics = ObservationStatistics.objects.create(
            comment='ObservationStatistics',
            observation_day=self.observation_day,
            observation_options=self.observation_options,
            observation_info=self.observation_info,

        )

    def test_create_observation_statistics(self):
        url = reverse('observation-statistics-create')
        data = {
            'comment': 'New ObservationStatistics',
            'observation_day': self.observation_day,
            'observation_options': self.observation_options,
            'observation_info': self.observation_info,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ObservationStatistics.objects.count(), 2)

    def test_retrieve_observation_statistics(self):
        url = reverse('observation-statistics', args=[self.observation_statistics.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'ObservationStatistics')

    def test_update_observation_statistics(self):
        url = reverse('observation-statistics-update', args=[self.observation_statistics.id])
        data = {
            'comment': 'Test ObservationStatistics',
            'observation_day': self.observation_day,
            'observation_options': self.observation_options,
            'observation_info': self.observation_info,
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Test ObservationStatistics')

    def test_delete_observation_statistics(self):
        url = reverse('observation-statistics-delete', args=[self.observation_statistics.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ObservationDayModelTest(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Test Branch", number=1)
        self.language = Language.objects.create(name="English")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.teacher = Teacher.objects.create(
            user=self.user,
            subject=self.subject,
            color='blue',
            total_students=10
        )
        self.group = Group.objects.create(
            name='Test group',
            branch=self.branch,
        )
        self.observation_day = ObservationDay.objects.create(
            day="2022-04-07",
            average=212,
            comment='ObservationDay',
            user=self.user,
            group=self.group,
            teacher=self.teacher,
        )

    def test_observation_day_creation(self):
        self.assertEqual(self.observation_day.comment, "ObservationDay")


class ObservationDayAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.branch = Branch.objects.create(name="Test Branch", number=1)
        self.language = Language.objects.create(name="English")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.client.login(username="testuser", password="testpassword")
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.teacher = Teacher.objects.create(
            user=self.user,
            subject=self.subject,
            color='blue',
            total_students=10
        )
        self.group = Group.objects.create(
            name='Test group',
            branch=self.branch,
        )
        self.observation_day = ObservationDay.objects.create(
            day="2022-04-07",
            average=212,
            comment='ObservationDay',
            user=self.user,
            group=self.group,
            teacher=self.teacher,
        )

    def test_create_observation_day(self):
        url = reverse('observation-day-create')
        data = {
            'day': "2022-04-07",
            'average': 234,
            'comment': 'New ObservationDay',
            'user': self.user,
            'group': self.group,
            'teacher': self.teacher,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ObservationDay.objects.count(), 2)

    def test_retrieve_observation_day(self):
        url = reverse('observation-day', args=[self.observation_day.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'ObservationDay')

    def test_update_observation_day(self):
        url = reverse('observation-day-update', args=[self.observation_day.id])
        data = {
            'day': "2022-04-07",
            'average': 234,
            'comment': 'Test ObservationDay',
            'user': self.user,
            'group': self.group,
            'teacher': self.teacher,
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], 'Test ObservationDay')

    def test_delete_observation_day(self):
        url = reverse('observation-day-delete', args=[self.observation_day.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


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
        data = {'name': 'ObservationOptions', 'value': 2}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'ObservationOptions')
        self.assertEqual(response.data['value'], 2)


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
