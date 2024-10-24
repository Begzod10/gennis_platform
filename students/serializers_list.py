from datetime import date

from django.db.models import Sum
from rest_framework import serializers

from attendances.models import AttendancePerMonth
from branch.models import Branch
from classes.models import ClassNumber
from group.models import Group, GroupReason
from group.serializers import GroupSerializer, GroupReasonSerializers, BranchSerializer, LanguageSerializers, \
    SubjectLevelSerializer, SystemSerializers, CourseTypesSerializers
from language.models import Language
from payments.models import PaymentTypes
from payments.serializers import PaymentTypesSerializers
from subjects.serializers import Subject
from subjects.serializers import SubjectSerializer
from teachers.models import TeacherGroupStatistics, TeacherBlackSalary, Teacher
from teachers.serializers import TeacherSerializer, TeacherSerializerRead
from user.serializers import UserSerializerWrite, UserSerializerRead
from .models import (Student, StudentHistoryGroups, StudentCharity, StudentPayment, DeletedStudent, DeletedNewStudent)


class StudentPaymentListSerializerTest(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name',
                                         read_only=True)
    student_surname = serializers.CharField(source='student.user.surname',
                                            read_only=True)
    payment_type_name = serializers.CharField(source='payment_type.name',
                                              read_only=True)
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = StudentPayment
        fields = ['id', 'student_name', 'student_surname', 'payment_type_name', 'payment_sum', 'status', 'added_data',
                  'date']
