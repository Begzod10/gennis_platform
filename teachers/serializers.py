from rest_framework import serializers

from subjects.serializers import SubjectSerializer
from user.serializers import UserSerializer
from .models import (Teacher, TeacherSalaryList, TeacherSalary, TeacherGroupStatistics, Subject)


class TeacherGroupStatisticsSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeacherGroupStatistics
        fields = '__all__'


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'color', 'total_students', 'id']


    def create(self, validated_data):
        user_data = validated_data.pop('user')

        subject_data = validated_data.pop('subject')

        subject = Subject.objects.get(name=subject_data['name'])

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        teacher = Teacher.objects.create(user=user, **validated_data, subject=subject)
        return teacher

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


class TeacherSalarySerializers(serializers.ModelSerializer):
    class Meta:
        model = TeacherSalary
        fields = '__all__'


class TeacherSalaryListSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeacherSalaryList
        fields = '__all__'

    def create(self, validated_data):
        payment_id = validated_data.get('payment')

        teacher_salary = validated_data.get('salary_id')
        teacher_salary.taken_salary += validated_data.get('salary')
        teacher_salary.remaining_salary -= validated_data.get('salary')
        teacher_salary.save()

        teacher_salary_list = TeacherSalaryList.objects.create(
            teacher=validated_data.get('teacher'),
            salary_id=validated_data.get('salary_id'),
            payment=payment_id,
            branch=validated_data.get('branch'),
            salary=validated_data.get('salary'),
            date=validated_data.get('date'),
            comment=validated_data.get('comment', ''),
            deleted=validated_data.get('deleted'),
        )
        return teacher_salary_list

    def update(self, instance, validated_data):
        instance.payment = validated_data.get('payment', instance.payment)
        instance.save()
        return instance
