from rest_framework import serializers

from branch.serializers import BranchSerializer, Branch
from payments.serializers import PaymentTypesSerializers, PaymentTypes
from subjects.serializers import SubjectSerializer
from user.serializers import UserSerializerWrite,UserSerializerRead
from .models import (Teacher, TeacherSalaryList, TeacherSalary, TeacherGroupStatistics, Subject, TeacherSalaryType)


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializerWrite()
    subject = SubjectSerializer()

    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'color', 'total_students', 'id']

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        subject_data = validated_data.pop('subject')

        subject = Subject.objects.get(name=subject_data['name'])

        user_serializer = UserSerializerWrite(data=user_data)
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


class TeacherSalaryTypeSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = TeacherSalaryType
        fields = "__all__"


class TeacherSerializerRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    subject = SubjectSerializer(read_only=True)
    teacher_salary_type = TeacherSalaryTypeSerializerRead(read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"


class TeacherSalaryReadSerializers(serializers.ModelSerializer):
    teacher = TeacherSerializerRead(read_only=True)
    branch = BranchSerializer(read_only=True)
    teacher_salary_type = TeacherSalaryTypeSerializerRead(read_only=True)

    class Meta:
        model = TeacherSalary
        fields = '__all__'


class TeacherSalaryCreateSerializers(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    teacher_salary_type = serializers.PrimaryKeyRelatedField(queryset=TeacherSalaryType.objects.all())

    class Meta:
        model = TeacherSalary
        fields = '__all__'


class TeacherGroupStatisticsReadSerializers(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    reason = serializers.SerializerMethodField()
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = TeacherGroupStatistics
        fields = '__all__'

    def get_reason(self, obj):
        from group.serializers import GroupReasonSerializers
        return GroupReasonSerializers(obj.reason).data


class TeacherSalaryListReadSerializers(serializers.ModelSerializer):
    teacher = TeacherSerializerRead(read_only=True)
    salary_id = TeacherSalaryReadSerializers(read_only=True)
    payment = PaymentTypesSerializers(read_only=True)

    branch = BranchSerializer(read_only=True)

    class Meta:
        model = TeacherSalaryList
        fields = '__all__'


class TeacherSalaryListCreateSerializers(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    salary_id = serializers.PrimaryKeyRelatedField(queryset=TeacherSalary.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())

    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = TeacherSalaryList
        fields = '__all__'
