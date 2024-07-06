from rest_framework import serializers


from .models import (Teacher)
from user.serializers import UserSerializer, CustomUser


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Teacher
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUser.objects.create(**user_data)
        student = Teacher.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
