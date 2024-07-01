# from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers

# from students.serializers import UserSerializer
from user.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname', 'username', 'father_name', 'password', 'birth_date', 'image',
                  'parent_name', 'email', 'data_joined'
                                          'phone', 'age', 'profile_img', 'observer', 'comment', 'registered_date']
