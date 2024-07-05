from rest_framework import serializers

from user.serializers import UserSerializer
from .models import (Student, CustomUser, StudentHistoryGroups, StudentCharity)


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'total_payment_month', 'shift', 'debt_status', 'subject']

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


class StudentCharitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCharity
        fields = '__all__'
