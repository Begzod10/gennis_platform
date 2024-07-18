from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from subjects.models import Subject
from branch.models import Branch
from payments.models import PaymentTypes
from .models import Teacher, TeacherSalary, TeacherSalaryList, TeacherGroupStatistics
import datetime
from language.models import Language
from django.utils import timezone

User = get_user_model()


class TeacherAPITestCase(APITestCase):

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
        self.teacher = Teacher.objects.create(
            user=self.user,
            subject=self.subject,
            color='blue',
            total_students=10
        )
        self.teacher_salary = TeacherSalary.objects.create(
            teacher=self.teacher,
            total_salary=1000,
            remaining_salary=500,
            taken_salary=500,
            branch=self.branch
        )
        self.payment = PaymentTypes.objects.create(name='Cash')

    def test_create_teacher(self):
        url = reverse('teacher-list-create')
        data = {
            'user': {
                'username': 'newuser',
                'password': 'newpass',
                # 'birth_date': timezone.now().isoformat(),
                'language': {
                    'name':self.language.name,
                    'id': self.language.id
                },
                'branch': {
                    'name': self.branch.name,

                    'id': self.branch.id
                }
            },
            'subject': {
                'name': self.subject.name
            },
            'color': 'red',
            'total_students': 20
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Teacher.objects.count(), 2)
        self.assertEqual(Teacher.objects.get(id=response.data['id']).color, 'red')

    def test_update_teacher(self):
        url = reverse('teacher-detail', args=[self.teacher.id])
        data = {
            'color': 'green',
            'total_students': 30
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.color, 'green')
        self.assertEqual(self.teacher.total_students, 30)

    def test_delete_teacher(self):
        url = reverse('teacher-detail', args=[self.teacher.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Teacher.objects.count(), 0)

    def test_create_teacher_salary_list(self):
        url = reverse('teacher-salary-list')
        data = {
            'teacher': self.teacher.id,
            'salary_id': self.teacher_salary.id,
            'payment': self.payment.id,
            'branch': self.branch.id,
            'salary': 100,
            'comment': 'Test salary list',
            'deleted': False  # Added default value
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch_id')
        if branch_id:
            return TeacherGroupStatistics.objects.filter(branch_id=branch_id)
        return TeacherGroupStatistics.objects.all()
