from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from location.models import Location
from system.models import System
from .models import Branch, Room, RoomImages, RoomSubject
from subjects.models import Subject


class RoomTests(APITestCase):
    def setUp(self):
        self.system = System.objects.create(number=1, name='Test System')
        self.location = Location.objects.create(name='Test Location', number=1, system=self.system)
        self.branch = Branch.objects.create(name='Test Branch', number=1, location=self.location)
        self.room = Room.objects.create(
            name='Test Room',
            seats_number=20,
            branch=self.branch,
            electronic_board=True,
            deleted=False
        )

        self.room_url = reverse('room-list-create')
        self.room_detail_url = reverse('room-retrieve-update-destroy', kwargs={'pk': self.room.pk})

    def test_create_room(self):
        data = {
            'name': 'New Room',
            'seats_number': 25,
            'branch_id': self.branch.id,
            'electronic_board': 'True',
            'deleted': 'False'
        }
        response = self.client.post(self.room_url, data, format='json')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 2)
        self.assertEqual(Room.objects.latest('id').name, 'New Room')

    def test_retrieve_room(self):
        response = self.client.get(self.room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['room']['name'], 'Test Room')

    def test_update_room(self):
        data = {'name': 'Updated Room'}
        response = self.client.patch(self.room_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertEqual(self.room.name, 'Updated Room')

    def test_delete_room(self):
        response = self.client.delete(self.room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertTrue(self.room.deleted)


class RoomImagesTests(APITestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name='Test Branch', number=1)
        self.room = Room.objects.create(
            name='Test Room',
            seats_number=20,
            branch=self.branch,
            electronic_board=True,
            deleted=False
        )
        self.image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'file_content',
            content_type='image/jpeg'
        )
        self.room_image = RoomImages.objects.create(
            image=self.image_file,
            room=self.room
        )
        self.room_images_url = reverse('room-images-list-create')
        self.room_images_detail_url = reverse('room-images-retrieve-update-destroy', kwargs={'pk': self.room_image.pk})

    def test_create_room_image(self):
        with open('media/room_images/brand_logo.jpg', 'rb') as img:
            image_file = SimpleUploadedFile(name='new_image.jpg', content=img.read(), content_type='image/jpeg')

        data = {
            'image': image_file,
            'room': self.room.pk
        }
        response = self.client.post(self.room_images_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RoomImages.objects.count(), 2)

    def test_retrieve_room_image(self):
        response = self.client.get(self.room_images_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_room_image(self):
        with open('media/room_images/brand_logo.jpg', 'rb') as img:
            image_file = SimpleUploadedFile(name='updated_image.jpg', content=img.read(), content_type='image/jpeg')
        data = {'image': image_file}
        response = self.client.patch(self.room_images_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room_image.refresh_from_db()
        # self.assertIn('updated_image.jpg', self.room_image.image.name)

    def test_delete_room_image(self):
        response = self.client.delete(self.room_images_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RoomImages.objects.count(), 0)


class RoomSubjectTests(APITestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name='Test Branch', number=1)
        self.room = Room.objects.create(
            name='Test Room',
            seats_number=20,
            branch=self.branch,
            electronic_board=True,
            deleted=False
        )
        self.subject = Subject.objects.create(name='Test Subject')
        self.room_subject = RoomSubject.objects.create(
            subject=self.subject,
            room=self.room
        )
        self.room_subject_url = reverse('room-subjects-list-create')
        self.room_subject_detail_url = reverse('room-subjects-retrieve-update-destroy',
                                               kwargs={'pk': self.room_subject.pk})

    def test_create_room_subject(self):
        data = {
            'subject': self.subject.pk,
            'room': self.room.pk
        }
        response = self.client.post(self.room_subject_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RoomSubject.objects.count(), 2)

    def test_retrieve_room_subject(self):
        response = self.client.get(self.room_subject_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], self.subject.pk)

    def test_update_room_subject(self):
        new_subject = Subject.objects.create(name='New Subject')
        data = {'subject': new_subject.pk}
        response = self.client.patch(self.room_subject_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room_subject.refresh_from_db()
        self.assertEqual(self.room_subject.subject, new_subject)

    def test_delete_room_subject(self):
        response = self.client.delete(self.room_subject_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RoomSubject.objects.count(), 0)
