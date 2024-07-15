from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book, BookImage
from .serializers import BookSerializer, BookImageSerializer


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
