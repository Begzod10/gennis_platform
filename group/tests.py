from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import CustomUser
from .models import Group
from students.models import Student
from branch.models import Branch
from language.models import Language
from subjects.models import Subject, SubjectLevel
from teachers.models import Teacher
from system.models import System


class GroupTests(APITestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Test Branch", number=1)
        self.language = Language.objects.create(name="English")
        self.system = System.objects.create(name="System", number=3245)
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.client.login(username="testuser", password="testpassword")
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.level = SubjectLevel.objects.create(name='Mathematics', subject=self.subject)
        self.student = Student.objects.create(
            user=self.user,
            subject=self.subject,
            shift='1'
        )
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
        self.group.students.add(self.student)
        self.group.teacher.add(self.teacher)
        self.group_data = {
            'name': 'Test group',
            'price': '1241234',
            'subject': self.subject.id,
            'students': [self.student.id],
            'teacher': self.teacher.id,
            'language': {
                'name': self.language.name,
                'id': self.language.id
            },
            'branch': {
                'name': self.branch.name,
                'id': self.branch.id,
                'number': 1
            },
            'teacher_salary': 324234,
            'attendance_days': 1234123,
            'system': self.system.id,
            'level': self.level.id
        }

    # def test_create_group(self):
    #     url = reverse('create')
    #     response = self.client.post(url, self.group_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(Group.objects.count(), 2)

    def test_get_group(self):
        url = reverse('create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_group_detail(self):
        url = reverse('profile', args=[self.group.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.group.name)

    # def test_update_group(self):
    #     url = reverse('user-detail', args=[self.user.id])
    #     updated_data = self.group_data.copy()
    #     updated_data['name'] = 'New group'
    #     response = self.client.put(url, updated_data, format='json')
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.user.refresh_from_db()
    #     self.assertEqual(self.user.username, 'New group')

    def test_delete_group(self):
        url = reverse('delete', args=[self.group.id])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
