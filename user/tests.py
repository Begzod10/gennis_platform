from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from user.models import CustomUser, Branch, Language

User = get_user_model()
from rest_framework.test import APITestCase
from user.serializers import UserSerializer
from user.models import CustomUser, Branch, Language


class UserSerializerTests(APITestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Test Branch", number=1)  # Add the number field
        self.language = Language.objects.create(name="English")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(),
                              ['id', 'name', 'surname', 'username', 'father_name', 'phone', 'age', 'profile_img',
                               'observer', 'comment', 'registered_date', 'birth_date', 'language', 'branch',
                               'is_superuser', 'is_staff'])

    def test_username_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['username'], self.user.username)

    def test_branch_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['branch']['name'], self.branch.name)

    def test_language_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['language']['name'], self.language.name)


class UserTests(APITestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Test Branch", number=1)  # Add the number field
        self.language = Language.objects.create(name="English")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            branch=self.branch,
            language=self.language,
        )
        self.client.login(username="testuser", password="testpassword")
        self.user_data = {
            'username': 'newuser',
            'password': 'newpassword',
            'branch': {'name': 'Test Branch'},
            'language': {'name': 'English'},
        }

    def test_create_user(self):
        url = reverse('user-list-create')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)





    def test_update_user(self):
        url = reverse('user-detail', args=[self.user.id])
        updated_data = self.user_data.copy()
        updated_data['username'] = 'updateduser'
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_delete_user(self):
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CustomUser.objects.count(), 0)


