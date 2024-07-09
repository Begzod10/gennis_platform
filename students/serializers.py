from rest_framework import serializers

from group.models import StudentHistoryGroups
from user.serializers import UserSerializer
from .models import (Student, CustomUser, StudentCharity, StudentPayment)
from django.utils.timezone import now


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'total_payment_month', 'shift', 'debt_status', 'subject', 'id']

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


class StudentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPayment
        fields = '__all__'

    def create(self, validated_data):
        total_debt = 400
        remaining_debt = 300
        payment = 100
        print(**validated_data)
        student = Student.objects.get(pk=validated_data.get('student_id'))
        current_year = now().year
        current_month = now().month
        student_payment = StudentPayment.objects.create(**validated_data)
        remaining_debt -= student_payment.payment_sum
        payment += student_payment.payment_sum
        if remaining_debt == 0:
            student.debt_status = 0
        elif student.total_payment_month > total_debt:
            student.debt_status = 1
        elif student.total_payment_month < total_debt:
            student.debt_status = 2
        student.save()
        return student_payment

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
