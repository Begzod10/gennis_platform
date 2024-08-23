from rest_framework import serializers

from branch.serializers import Branch
from group.models import Group, Student
from payments.serializers import PaymentTypes
from teachers.models import (Teacher, TeacherSalaryList, TeacherSalary, TeacherSalaryType,TeacherBlackSalary)


class TransferTeacherSalaryCreateSerializers(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')
    teacher_salary_type = serializers.SlugRelatedField(queryset=TeacherSalaryType.objects.all(), slug_field='old_id',
                                                       allow_null=True)

    class Meta:
        model = TeacherSalary
        fields = '__all__'


class TransferTeacherSalaryListCreateSerializers(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id')
    salary_id = serializers.SlugRelatedField(queryset=TeacherSalary.objects.all(), slug_field='old_id', allow_null=True)
    payment = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')

    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')

    class Meta:
        model = TeacherSalaryList
        fields = '__all__'


class TransferTeacherBlackSalaryCreateSerializers(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id')
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id', allow_null=True)
    student = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id')

    class Meta:
        model = TeacherBlackSalary
        fields = '__all__'
