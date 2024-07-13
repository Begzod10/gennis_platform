from django.utils.timezone import now
from rest_framework import serializers

from attendance.models import AttendancePerMonth
from subjects.serializers import SubjectSerializer, Subject
from teachers.models import TeacherGroupStatistics
from user.serializers import UserSerializer
from .models import (Student, CustomUser, StudentHistoryGroups, StudentCharity, StudentPayment, DeletedStudent)


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    subject = SubjectSerializer()
    parents_number = serializers.CharField(write_only=True)
    shift = serializers.CharField(write_only=True)

    # subject_id = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['user', 'subject', 'parents_number', 'shift']

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        subject_data = validated_data.pop('subject')
        subject = Subject.objects.get(name=subject_data['name'])

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        student = Student.objects.create(user=user, **validated_data, subject=subject)
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
        attendance_per_month = AttendancePerMonth.objects.get(student=validated_data.get('student_id'))
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

    def delete(self, instance):
        # instance.deleted = True
        # instance.save()
        # instance.user_salary.taken_salary -= instance.salary
        # instance.user_salary.remaining_salary += instance.salary
        # instance.user_salary.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DeletedStudentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = DeletedStudent
        fields = '__all__'

    def create(self, validated_data):
        deleted_student = DeletedStudent.objects.create(**validated_data)
        teacher_group_statistics = TeacherGroupStatistics.objects.get(teacher=validated_data.get('teacher'),
                                                                      group_reason=validated_data.get(
                                                                          'group_reason'))
        if teacher_group_statistics:
            deleted_students_number = len(DeletedStudent.objects.get(teacher=validated_data.get('teacher')).all()) / 100

            number_students = len(DeletedStudent.objects.get(reason=validated_data.get('group_reason'),
                                                             teacher=validated_data.get('teacher')).all())
            percentage = deleted_students_number * number_students
            teacher_group_statistics.number_students = number_students
            teacher_group_statistics.percentage = percentage
            teacher_group_statistics.save()
        else:
            deleted_students_number = len(DeletedStudent.objects.get(teacher=validated_data.get('teacher')).all()) / 100

            number_students = 1
            percentage = deleted_students_number * number_students
            TeacherGroupStatistics.objects.create(teacher=validated_data.get('teacher'),
                                                  reason=validated_data.get('group_reason'),
                                                  branch=validated_data.get('branch'),
                                                  number_students=number_students, percentage=percentage)
        return deleted_student
