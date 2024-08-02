# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.contrib.auth import get_user_model
# from subjects.models import Subject
# from branch.models import Branch
# from payments.models import PaymentTypes
# from .models import Student, StudentCharity
# import datetime
# from language.models import Language
# from django.utils import timezone
# from group.models import Group
#
# User = get_user_model()
#
#
# class StudentAPITestCase(APITestCase):
#
#     def setUp(self):
#         self.branch = Branch.objects.create(name='Main Branch', number=1)
#         self.language = Language.objects.create(name='English')
#         self.group = Group.objects.create(name='Test Group')
#         self.user = User.objects.create_user(
#             username='testusejnbvr',
#             password='testpass',
#             birth_date=timezone.make_aware(datetime.datetime(2000, 1, 1)),
#             branch=self.branch,
#             language=self.language
#         )
#         self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
#         self.student = Student.objects.create(
#             user=self.user,
#             subject=self.subject,
#             shift='1'
#         )
#         self.student_charity = StudentCharity.objects.create(
#             student=self.student,
#             charity_sum=1000,
#             group=self.group
#         )
#         self.payment = PaymentTypes.objects.create(name='Cash')
#
#     def test_create_student(self):
#         url = reverse('student-list-create')
#         data = {
#             'user': {
#                 'username': 'newuser',
#                 'password': 'newpass',
#                 # 'birth_date': timezone.now().isoformat(),
#                 'language': {
#                     'name':self.language.name,
#                     'id': self.language.id
#                 },
#                 'branch': {
#                     'name': self.branch.name,
#
#                     'id': self.branch.id
#                 }
#             },
#             'subject': {
#                 'name': self.subject.name
#             },
#             'shift': '1',
#             'parents_number': '1231'
#         }
#         response = self.client.post(url, data, format='json')
#         print(response.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Student.objects.count(), 2)
#
#     def test_update_student(self):
#         url = reverse('student-detail', args=[self.student.id])
#         data = {
#             'shift': '2'
#         }
#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.student.refresh_from_db()
#         self.assertEqual(self.student.shift, '2')
#
#     # def test_create_student_payment(self):
#     #     url = reverse('student-payment-list-create')
#     #     data = {
#     #         'student': self.student.id,
#     #         'payment_type': self.payment.id,
#     #         'payment_sum': 200,
#     #         'status': False
#     #     }
#     #     print(data)
#     #
#     #     response = self.client.post(url, data, format='json')
#     #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
