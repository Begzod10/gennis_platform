from rest_framework import serializers

from branch.serializers import BranchSerializer, Branch
from payments.serializers import PaymentTypesSerializers, PaymentTypes
from subjects.serializers import SubjectSerializer
from system.models import System
from system.serializers import SystemSerializers
from user.serializers import UserSerializerWrite, UserSerializerRead, Language
from .models import (Teacher, TeacherSalaryList, TeacherSalary, TeacherGroupStatistics, Subject, TeacherSalaryType)
from .models import (TeacherAttendance)


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializerWrite()
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)

    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'color', 'total_students', 'id']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subject_data = validated_data.pop('subject')
        if isinstance(user_data.get('language'), Language):
            user_data['language'] = user_data['language'].id
        if isinstance(user_data.get('branch'), Branch):
            user_data['branch'] = user_data['branch'].id

        user_serializer = UserSerializerWrite(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        teacher = Teacher.objects.create(user=user, **validated_data)
        teacher.subject.set(subject_data)
        branch = Branch.objects.get(pk=user_data['branch'])
        teacher.branches.set(branch)
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


class TeacherAttendanceSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all())
    day = serializers.DateTimeField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = TeacherAttendance
        fields = ['id', 'teacher', 'system', 'day', 'status']


class TeacherAttendanceListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    teacher = TeacherSerializer(required=False)
    system = SystemSerializers(required=False)
    day = serializers.DateTimeField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = TeacherAttendance
        fields = ['id', 'teacher', 'system', 'day', 'status']


class TeacherGroupStatisticsSerializers(serializers.ModelSerializer):
    class Meta:
        model = TeacherGroupStatistics
        fields = '__all__'


class TeacherSalaryTypeSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = TeacherSalaryType
        fields = "__all__"


class TeacherSerializerRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    subject = SubjectSerializer(many=True)
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
    salary_id = serializers.PrimaryKeyRelatedField(queryset=TeacherSalary.objects.all())

    class Meta:
        model = TeacherSalaryList
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
    date = serializers.SerializerMethodField(read_only=True)

    payment = PaymentTypesSerializers(read_only=True)

    branch = BranchSerializer(read_only=True)

    class Meta:
        model = TeacherSalaryList
        fields = '__all__'

    def get_date(self, obj):
        return obj.date.strftime('%Y-%m-%d %H:%M')


class TeacherSalaryListCreateSerializers(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    salary_id = serializers.PrimaryKeyRelatedField(queryset=TeacherSalary.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    name = serializers.SerializerMethodField(required=False, read_only=True)
    surname = serializers.SerializerMethodField(required=False, read_only=True)
    date = serializers.SerializerMethodField(required=False, read_only=True)
    payment_type_name = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = TeacherSalaryList
        fields = '__all__'
    def get_name(self, obj):
        return obj.teacher.user.name

    def get_surname(self, obj):
        return obj.teacher.user.surname

    def get_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def get_payment_type_name(self, obj):
        return obj.payment.name
    def create(self, validated_data):
        teacher = validated_data.get('teacher')
        salary_id = validated_data.get('salary_id')
        salary_amount = validated_data.get('salary')

        if salary_id:
            salary_id.taken_salary += salary_amount
            salary_id.remaining_salary -= salary_amount
            salary_id.save()

        teacher_salary_list = TeacherSalaryList.objects.create(
            teacher=teacher,
            salary_id=salary_id,
            payment=validated_data.get('payment'),
            branch=validated_data.get('branch'),
            salary=salary_amount,
            deleted=False,
            comment=validated_data.get('comment', ''),
        )
        return teacher_salary_list

    def update(self, instance, validated_data):
        salary_id = validated_data.get('salary_id', instance.salary_id)
        salary_amount = validated_data.get('salary', instance.salary)

        if salary_id != instance.salary_id:
            if instance.salary_id:
                instance.salary_id.taken_salary -= instance.salary
                instance.salary_id.remaining_salary += instance.salary
                instance.salary_id.save()
            salary_id.taken_salary += salary_amount
            salary_id.remaining_salary -= salary_amount
            salary_id.save()

        instance.teacher = validated_data.get('teacher', instance.teacher)
        instance.salary_id = salary_id
        instance.payment = validated_data.get('payment', instance.payment)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.salary = salary_amount
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance


