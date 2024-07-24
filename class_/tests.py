from django.test import TestCase
from rest_framework.test import APIClient
from .models import ClassTypes, ClassNumber, ClassCoin, ClassColors, CoinInfo, StudentCoin
from django.urls import reverse
from rest_framework import status
from subjects.models import Subject
from branch.models import Branch
from students.models import Student
import datetime
from django.contrib.auth import get_user_model
from language.models import Language
from django.utils import timezone
from group.models import Group

User = get_user_model()


class StudentCoinModelTest(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name='Main Branch', number=1)
        self.language = Language.objects.create(name='English')
        self.user = User.objects.create_user(
            username='testusejnbvr',
            password='testpass',
            birth_date=timezone.make_aware(datetime.datetime(2000, 1, 1)),
            branch=self.branch,
            language=self.language
        )
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.group = Group.objects.create(name="New Group")
        self.student = Student.objects.create(
            user=self.user,
            subject=self.subject,
            shift='1'
        )

        self.class_coin = ClassCoin.objects.create(
            total_coin=3442,
            given_coin=7686,
            remaining_coin=678334,
            month_date="2024-07-12",
            group=self.group
        )

        self.student_coin = StudentCoin.objects.create(
            value="Test StudentCoin",
            class_coin=self.class_coin,
            student=self.student
        )

    def test_class_coin_creation(self):
        self.assertEqual(self.student_coin.value, "Test StudentCoin")
        self.assertEqual(self.student_coin.class_coin, self.class_coin)
        self.assertEqual(self.student_coin.student, self.student)


class StudentCoinAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.group = Group.objects.create(name="New Group")
        self.student = Student.objects.first()

        self.class_coin = ClassCoin.objects.create(
            total_coin=3442,
            given_coin=7686,
            remaining_coin=678334,
            month_date="2024-07-12",
            group=self.group
        )
        self.branch = Branch.objects.create(name='Main Branch', number=1)
        self.language = Language.objects.create(name='English')
        self.group = Group.objects.create(name='Test Group')
        self.user = User.objects.create_user(
            username='testusejnbvr',
            password='testpass',
            birth_date=timezone.make_aware(datetime.datetime(2000, 1, 1)),
            branch=self.branch,
            language=self.language
        )
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.student = Student.objects.create(
            user=self.user,
            subject=self.subject,
            shift='1'
        )

        self.student_coin = StudentCoin.objects.create(
            value="Test StudentCoin",
            class_coin=self.class_coin,
            student=self.student
        )

    def test_create_student_coin(self):
        url = reverse('student-coin-create')
        data = {
            'value': 'New StudentCoin',
            'class_coin': self.class_coin.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentCoin.objects.count(), 2)

    def test_retrieve_student_coin(self):
        url = reverse('student-coin', args=[self.student_coin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'Test StudentCoin')

    def test_update_student_coin(self):
        url = reverse('student-coin-update', args=[self.student_coin.id])
        data = {'value': 'StudentCoin'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'StudentCoin')

    def test_delete_student_coin(self):
        url = reverse('student-coin-delete', args=[self.student_coin.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StudentCoin.objects.count(), 0)


class CoinInfoModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="New Group")

        self.class_coin = ClassCoin.objects.create(
            total_coin=3442,
            given_coin=7686,
            remaining_coin=678334,
            month_date="2024-07-12",
            group=self.group
        )

        self.coin_info = CoinInfo.objects.create(
            value="Test CoinInfo",
            reason="Test CoinInfo reason",
            day_date='2024-07-12',
            class_coin=self.class_coin
        )

    def test_class_coin_creation(self):
        self.assertEqual(self.coin_info.value, "Test CoinInfo")
        self.assertEqual(self.coin_info.reason, "Test CoinInfo reason")
        self.assertEqual(self.coin_info.day_date, "2024-07-12")
        self.assertEqual(self.coin_info.class_coin, self.class_coin)


class CoinInfoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.group = Group.objects.create(name="New Group")

        self.class_coin = ClassCoin.objects.create(
            total_coin=3442,
            given_coin=7686,
            remaining_coin=678334,
            month_date="2024-07-12",
            group=self.group
        )

        self.coin_info = CoinInfo.objects.create(
            value="Test CoinInfo",
            reason="Test CoinInfo reason",
            day_date='2024-07-12',
            class_coin=self.class_coin
        )

    def test_create_coin_info(self):
        url = reverse('coin-info-create')
        data = {
            'value': 'New CoinInfo',
            'reason': 'New CoinInfo reason',
            'day_date': "2024-07-12",
            'class_coin': self.class_coin.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CoinInfo.objects.count(), 2)

    def test_retrieve_coin_info(self):
        url = reverse('coin-info', args=[self.coin_info.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'Test CoinInfo')

    def test_update_coin_info(self):
        url = reverse('coin-info-update', args=[self.coin_info.id])
        data = {'value': 'CoinInfo'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'CoinInfo')

    def test_delete_coin_info(self):
        url = reverse('coin-info-delete', args=[self.coin_info.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CoinInfo.objects.count(), 0)


class ClassCoinModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="New Group")

        self.class_coin = ClassCoin.objects.create(
            total_coin=3442,
            given_coin=7686,
            remaining_coin=678334,
            month_date="2024-07-12",
            group=self.group
        )

    def test_class_coin_creation(self):
        self.assertEqual(self.class_coin.total_coin, 3442)
        self.assertEqual(self.class_coin.given_coin, 7686)
        self.assertEqual(self.class_coin.remaining_coin, 678334)
        self.assertEqual(self.class_coin.month_date, "2024-07-12")
        self.assertEqual(self.class_coin.group, self.group)


class ClassCoinAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.group = Group.objects.create(name="New Group")

        self.class_coin = ClassCoin.objects.create(
            total_coin=3442,
            given_coin=7686,
            remaining_coin=678334,
            month_date="2024-07-12",
            group=self.group
        )

    def test_create_class_coin(self):
        url = reverse('class-coin-create')
        data = {
            'total_coin': 3442,
            'given_coin': 7686,
            'remaining_coin': 678334,
            'month_date': "2024-07-12",
            'group': self.group.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClassCoin.objects.count(), 2)

    def test_retrieve_class_coin(self):
        url = reverse('class-coin', args=[self.class_coin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_coin'], 3442)

    def test_update_class_coin(self):
        url = reverse('class-coin-update', args=[self.class_coin.id])
        data = {'total_coin': 45654}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_coin'], 45654)

    def test_delete_class_coin(self):
        url = reverse('class-coin-delete', args=[self.class_coin.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ClassCoin.objects.count(), 0)


class ClassNumberModelTest(TestCase):
    def setUp(self):
        self.subjects = Subject.objects.create(name="Math", ball_number=10)
        self.class_types = ClassTypes.objects.create(
            name="Test ClassTypes",
        )
        self.class_number = ClassNumber.objects.create(
            number=31312,
            curriculum_hours=68767,
            class_types=self.class_types,
        )
        self.class_number.subjects.add(self.subjects)

    def test_class_number_creation(self):
        self.assertEqual(self.class_number.class_types, self.class_types)
        self.assertEqual(self.class_number.subjects.first(), self.subjects)
        self.assertEqual(self.class_number.number, 31312)
        self.assertEqual(self.class_number.curriculum_hours, 68767)


class ClassNumberAPITestCase(TestCase):
    def setUp(self):
        self.subjects = Subject.objects.create(name="Math", ball_number=10)
        self.class_types = ClassTypes.objects.create(
            name="Test ClassTypes",
        )
        self.class_number = ClassNumber.objects.create(
            number=31312,
            curriculum_hours=68767,
            class_types=self.class_types,
        )
        self.class_number.subjects.add(self.subjects)

    def test_create_class_number(self):
        url = reverse('class-number-create')
        data = {
            'class_types': self.class_types.id,
            'subjects': [self.subjects.id],
            'number': 31312,
            'curriculum_hours': 68767
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClassNumber.objects.count(), 2)

    def test_retrieve_class_number(self):
        url = reverse('class-number', args=[self.class_number.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number'], 31312)

    def test_update_class_number(self):
        url = reverse('class-number-update', args=[self.class_number.id])
        data = {'number': 345345}
        response = self.client.patch(url, data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['number'], 345345)

    def test_delete_class_number(self):
        url = reverse('class-number-delete', args=[self.class_number.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ClassNumber.objects.count(), 0)


class ClassColorsModelTest(TestCase):
    def setUp(self):
        self.class_colors = ClassColors.objects.create(
            name="Test ClassColors",
            value="fe2323"
        )

    def test_lead_creation(self):
        self.assertEqual(self.class_colors.name, "Test ClassColors")


class ClassColorsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.class_types = ClassColors.objects.create(
            name="Test ClassColors",
            value="fe2323",
        )

    def test_create_class_types(self):
        url = reverse('class_-colors-list-create')
        data = {
            'name': 'New ClassColors',
            'value': "fu564"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClassColors.objects.count(), 2)

    def test_retrieve_class_types(self):
        url = reverse('class_-colors-detail', args=[self.class_types.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test ClassColors')

    def test_update_class_types(self):
        url = reverse('class_-colors-detail', args=[self.class_types.id])
        data = {'name': 'Test ClassColors2'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test ClassColors2')

    def test_delete_class_types(self):
        url = reverse('class_-colors-detail', args=[self.class_types.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ClassTypes.objects.count(), 0)


class ClassTypesModelTest(TestCase):
    def setUp(self):
        self.class_types = ClassTypes.objects.create(
            name="Test ClassTypes",
        )

    def test_lead_creation(self):
        self.assertEqual(self.class_types.name, "Test ClassTypes")


class ClassTypesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.class_types = ClassTypes.objects.create(
            name="Test ClassTypes",
        )

    def test_create_class_types(self):
        url = reverse('class_-types-list-create')
        data = {
            'name': 'New ClassTypes',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClassTypes.objects.count(), 2)

    def test_retrieve_class_types(self):
        url = reverse('class_-types-detail', args=[self.class_types.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test ClassTypes')

    def test_update_class_types(self):
        url = reverse('class_-types-detail', args=[self.class_types.id])
        data = {'name': 'Test ClassTypes2'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test ClassTypes2')

    def test_delete_class_types(self):
        url = reverse('class_-types-detail', args=[self.class_types.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ClassTypes.objects.count(), 0)
