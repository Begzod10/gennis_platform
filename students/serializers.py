from rest_framework import serializers

from .models import (Student)
from group.models import StudentHistoryGroups
from user.serializers import CustomUser, UserSerializer


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUser.objects.create(**user_data)
        student = Student.objects.create(user=user, **validated_data)
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


class StudentHistoryGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentHistoryGroups
        fields = '__all__'

    def create(self, validated_data):
        student = StudentHistoryGroups.objects.create(**validated_data)
        return student

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
