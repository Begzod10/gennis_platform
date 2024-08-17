from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book, BookImage, BookOrder, BalanceOverhead, CenterBalance, BookOverhead, EditorBalance
from user.models import CustomUser
from branch.models import Branch
from language.models import Language
from subjects.models import Subject
from students.models import Student
from teachers.models import Teacher
from group.models import Group
from payments.models import PaymentTypes
from system.models import System
from location.models import Location


class BookOverheadTests(APITestCase):
    def setUp(self):
        self.payment_type = PaymentTypes.objects.create(name='Credit Card')
        self.editor_balance = EditorBalance.objects.create(
            balance=2000000,
            payment_type=self.payment_type
        )
        self.book_overhead = BookOverhead.objects.create(
            price=20000,
            name='scsdcd',
            editor_balance=self.editor_balance,
            payment_type=self.payment_type,
        )
        self.url_create = reverse('book-overhead-create')
        self.url_update = reverse('book-overhead-update', args=[self.book_overhead.id])
        self.url_delete = reverse('book-overhead-delete', args=[self.book_overhead.id])

    def test_create_balance_overhead(self):
        data = {
            'price': 300000,
            'name': 'A description of the new test balance_overhead',
            'editor_balance': self.editor_balance.id,
            'payment_type': self.payment_type.id,
        }
        response = self.client.post(self.url_create, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookOverhead.objects.count(), 2)
        self.assertEqual(BookOverhead.objects.latest('id').reason, 'A description of the new test balance_overhead')

    def test_update_balance_overhead(self):
        data = {
            'price': 200000,
            'name': 'Updated a description of the new test balance_overhead',
            'editor_balance': self.editor_balance.id,
            'payment_type': self.payment_type.id,
        }
        response = self.client.put(self.url_update, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_overhead.refresh_from_db()
        self.assertEqual(self.book_overhead.reason, 'Updated a description of the new test balance_overhead')

    def test_delete_balance_overhead(self):
        data = {
            'deleted_reason': 'dcsvus'
        }
        response = self.client.post(self.url_delete, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BalanceOverheadTests(APITestCase):
    def setUp(self):
        self.system = System.objects.create(name='Test System', number=1)
        self.location = Location.objects.create(
            name='Test Location',
            number=1,
            system=self.system
        )
        self.branch = Branch.objects.create(name="Test Branch", number=1, location=self.location)
        self.balance = CenterBalance.objects.create(
            total_money=2000000,
            remaining_money=2000000,
            taken_money=0,
            branch=self.branch,
        )
        self.payment_type = PaymentTypes.objects.create(name='Credit Card')
        self.balance_overhead = BalanceOverhead.objects.create(
            overhead_sum=20000,
            reason='scsdcd',
            branch=self.branch,
            payment_type=self.payment_type,
            balance=self.balance
        )
        self.url_create = reverse('balance-overhead-create')
        self.url_update = reverse('balance-overhead-update', args=[self.balance_overhead.id])
        self.url_delete = reverse('balance-overhead-delete', args=[self.balance_overhead.id])

    def test_create_balance_overhead(self):
        data = {
            'overhead_sum': 300000,
            'reason': 'A description of the new test balance_overhead',
            'branch': self.branch.id,
            'payment_type': self.payment_type.id,
            'balance': self.balance.id,
        }
        response = self.client.post(self.url_create, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BalanceOverhead.objects.count(), 2)
        self.assertEqual(BalanceOverhead.objects.latest('id').reason, 'A description of the new test balance_overhead')

    def test_update_balance_overhead(self):
        data = {
            'overhead_sum': 200000,
            'reason': 'Updated a description of the new test balance_overhead',
            'branch': self.branch.id,
            'payment_type': self.payment_type.id,
            'balance': self.balance.id
        }
        response = self.client.put(self.url_update, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.balance_overhead.refresh_from_db()
        self.assertEqual(self.balance_overhead.reason, 'Updated a description of the new test balance_overhead')

    def test_delete_balance_overhead(self):
        response = self.client.delete(self.url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookOrderTests(APITestCase):
    def setUp(self):
        self.system = System.objects.create(name='Test System', number=1)
        self.location = Location.objects.create(
            name='Test Location',
            number=1,
            system=self.system
        )
        self.branch = Branch.objects.create(name="Test Branch", number=1, location=self.location)
        self.language = Language.objects.create(name="English")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.subject = Subject.objects.create(name='Mathematics', ball_number=1)
        self.student = Student.objects.create(
            user=self.user,
            shift='1'
        )
        self.student.subject.set([self.subject])
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
        self.book = Book.objects.create(
            name="Test Book",
            desc="A description of the test book",
            price=100,
            own_price=80,
            share_price=90,
            file=None
        )
        self.book_order = BookOrder.objects.create(
            user=self.user,
            student=self.student,
            teacher=self.teacher,
            branch=self.branch,
            group=self.group,
            book=self.book,
            count=2,
            reason='scsdcd'
        )
        self.url_create = reverse('book-order-create')
        self.url_delete = reverse('book-order-delete', args=[self.book_order.id])

    def test_create_book_order(self):
        data = {
            'count': 1,
            'reason': 'A description of the new test book_order',
            'student': self.student.id,
            'teacher': self.teacher.id,
            'branch': self.branch.id,
            'user': self.user.id,
            'group': self.group.id,
            'book': self.book.id,
        }
        response = self.client.post(self.url_create, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookOrder.objects.count(), 2)
        self.assertEqual(BookOrder.objects.latest('id').reason, 'A description of the new test book_order')

    def test_delete_book_order(self):
        response = self.client.delete(self.url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookTests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            name="Test Book",
            desc="A description of the test book",
            price=100,
            own_price=80,
            share_price=90,
            file=None
        )
        self.url = reverse('book-list-create')
        self.url_detail = reverse('book-retrieve-update-destroy', args=[self.book.id])

    def test_create_book(self):
        data = {
            'name': 'New Test Book',
            'desc': 'A description of the new test book',
            'price': 150,
            'own_price': 120,
            'share_price': 130,
            'file': None
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.latest('id').name, 'New Test Book')

    def test_update_book(self):
        data = {
            'name': 'Updated Test Book',
            'desc': 'Updated description',
            'price': 200,
            'own_price': 180,
            'share_price': 190,
            'file': None
        }
        response = self.client.put(self.url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.name, 'Updated Test Book')

    def test_delete_book(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)


class BookImageTests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            name="Test Book",
            desc="A description of the test book",
            price=100,
            own_price=80,
            share_price=90,
            file=None
        )
        self.book_image = BookImage.objects.create(
            image=None,
            book=self.book
        )
        self.url = reverse('book-image-list-create')
        self.url_detail = reverse('book-image-retrieve-update-destroy', args=[self.book_image.id])

    def test_create_book_image(self):
        data = {
            'image': None,
            'book': self.book.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookImage.objects.count(), 2)
        self.assertEqual(BookImage.objects.latest('id').book, self.book)

    def test_update_book_image(self):
        data = {
            'image': None,
            'book': self.book.id
        }
        response = self.client.put(self.url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_image.refresh_from_db()
        self.assertEqual(self.book_image.book, self.book)

    def test_delete_book_image(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BookImage.objects.count(), 0)
