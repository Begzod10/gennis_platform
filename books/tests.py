from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book, BookImage, BookOrder, BalanceOverhead, CenterBalance
from .serializers import BookSerializer, BookImageSerializer, BookOrderSerializers, BalanceOverheadSerializers
from user.models import CustomUser
from branch.models import Branch
from language.models import Language
from subjects.models import Subject
from students.models import Student
from teachers.models import Teacher
from group.models import Group
from payments.models import PaymentTypes


class BalanceOverheadTests(APITestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Test Branch", number=1)
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
        self.url = reverse('balance-overhead-list-create')
        self.url_detail = reverse('balance-overhead-retrieve-update-destroy', args=[self.balance_overhead.id])

    def test_list_balance_overhead(self):
        response = self.client.get(self.url)
        balance_overheads = BalanceOverhead.objects.all()
        serializer = BalanceOverheadSerializers(balance_overheads, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_balance_overhead(self):
        data = {
            'overhead_sum': 300000,
            'reason': 'A description of the new test balance_overhead',
            'branch': self.branch,
            'payment_type': self.payment_type,
            'balance': self.balance
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BalanceOverhead.objects.count(), 2)
        self.assertEqual(BalanceOverhead.objects.latest('id').reason, 'A description of the new test balance_overhead')

    def test_retrieve_balance_overhead(self):
        response = self.client.get(self.url_detail)
        serializer = BalanceOverheadSerializers(self.balance_overhead)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_balance_overhead(self):
        data = {
            'overhead_sum': 200000,
            'reason': 'Updated a description of the new test balance_overhead',
            'branch': self.branch,
            'payment_type': self.payment_type,
            'balance': self.balance
        }
        response = self.client.put(self.url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.balance_overhead.refresh_from_db()
        self.assertEqual(self.balance_overhead.reason, 'Updated a description of the new test balance_overhead')

    def test_delete_balance_overhead(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookOrderTests(APITestCase):
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
        self.url = reverse('book-order-list-create')
        self.url_detail = reverse('book-order-retrieve-update-destroy', args=[self.book_order.id])

    def test_list_book_order(self):
        response = self.client.get(self.url)
        book_orders = BookOrder.objects.all()
        serializer = BookOrderSerializers(book_orders, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_book_order(self):
        data = {
            'count': 1,
            'reason': 'A description of the new test book_order',
            'student': self.student,
            'teacher': self.teacher,
            'branch': self.branch,
            'user': self.user,
            'group': self.group,
            'book': self.book,
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookOrder.objects.count(), 2)
        self.assertEqual(BookOrder.objects.latest('id').reason, 'A description of the new test book_order')

    def test_retrieve_book_order(self):
        response = self.client.get(self.url_detail)
        serializer = BookOrderSerializers(self.book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_book_order(self):
        data = {
            'count': 3,
            'reason': 'Updated a description of the new test book_order',
            'student': self.student,
            'teacher': self.teacher,
            'branch': self.branch,
            'user': self.user,
            'group': self.group,
            'book': self.book,
        }
        response = self.client.put(self.url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_order.refresh_from_db()
        self.assertEqual(self.book_order.reason, 'Updated a description of the new test book_order')

    def test_delete_book_order(self):
        response = self.client.delete(self.url_detail)
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

    def test_list_books(self):
        response = self.client.get(self.url)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

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

    def test_retrieve_book(self):
        response = self.client.get(self.url_detail)
        serializer = BookSerializer(self.book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

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

    def test_list_book_images(self):
        response = self.client.get(self.url)
        book_images = BookImage.objects.all()
        serializer = BookImageSerializer(book_images, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_book_image(self):
        data = {
            'image': None,
            'book': self.book.id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookImage.objects.count(), 2)
        self.assertEqual(BookImage.objects.latest('id').book, self.book)

    def test_retrieve_book_image(self):
        response = self.client.get(self.url_detail)
        serializer = BookImageSerializer(self.book_image)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

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
