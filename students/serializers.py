from rest_framework import serializers
from attendances.models import AttendancePerMonth
from subjects.serializers import Subject
from subjects.serializers import SubjectSerializer
from teachers.models import TeacherGroupStatistics, TeacherBlackSalary, Teacher
from teachers.serializers import TeacherSerializer
from user.serializers import UserSerializerWrite, CustomUser
from .models import (Student, StudentHistoryGroups, StudentCharity, StudentPayment, DeletedStudent, DeletedNewStudent)
from group.serializers import GroupSerializer, GroupReasonSerializers
from group.models import Group, GroupReason
from branch.models import Branch
from payments.models import PaymentTypes
from payments.serializers import PaymentTypesSerializers


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)
    parents_number = serializers.CharField()
    shift = serializers.CharField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'subject', 'parents_number', 'shift']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subject_data = validated_data.pop('subject')

        user_serializer = UserSerializerWrite(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        subjects = []
        for subj_data in subject_data:
            subject, created = Subject.objects.get_or_create(**subj_data)
            subjects.append(subject)

        student = Student.objects.create(user=user, parents_number=validated_data.get('parents_number'),
                                         shift=validated_data.get('shift'))
        student.subject.set(subjects)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        subject_data = validated_data.pop('subject', None)

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()

        if subject_data:
            subjects = []
            for subj_data in subject_data:
                subject, created = Subject.objects.get_or_create(**subj_data)
                subjects.append(subject)
            instance.subject.set(subjects)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StudentListSerializer(serializers.ModelSerializer):
    user = UserSerializerWrite()
    subject = SubjectSerializer(many=True)
    parents_number = serializers.CharField()
    shift = serializers.CharField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'subject', 'parents_number', 'shift']


class StudentHistoryGroupsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    reason = serializers.CharField(required=False)
    joined_day = serializers.DateTimeField(required=False)
    left_day = serializers.DateTimeField(required=False)

    class Meta:
        model = StudentHistoryGroups
        fields = ['id', 'student', 'group', 'teacher', 'reason', 'joined_day', 'left_day']

    def create(self, validated_data):
        student = StudentHistoryGroups.objects.create(**validated_data)
        return student

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StudentHistoryGroupsListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=True)
    group = GroupSerializer(required=True)
    teacher = TeacherSerializer(required=True)
    reason = serializers.CharField(required=False)
    joined_day = serializers.DateTimeField(required=False)
    left_day = serializers.DateTimeField(required=False)

    class Meta:
        model = StudentHistoryGroups
        fields = ['id', 'student', 'group', 'teacher', 'reason', 'joined_day', 'left_day']


class StudentCharitySerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    charity_sum = serializers.IntegerField(required=False)

    class Meta:
        model = StudentCharity
        fields = ['id', 'student', 'group', 'charity_sum']


class StudentCharityListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=True)
    group = GroupSerializer(required=True)
    charity_sum = serializers.IntegerField(required=False)

    class Meta:
        model = StudentCharity
        fields = ['id', 'student', 'group', 'charity_sum']


class StudentPaymentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = StudentPayment
        fields = ['id', 'student', 'payment_type', 'payment_sum', 'status']

    def create(self, validated_data):
        print(validated_data)
        attendance_per_months = AttendancePerMonth.objects.get(student=validated_data.get('student'),
                                                               status=False).all()
        student = Student.objects.get(pk=validated_data.get('student'))
        student_payment = StudentPayment.objects.create(**validated_data)
        payment_sum = student_payment.payment_sum + student_payment.extra_payment
        for attendance_per_month in attendance_per_months:
            if attendance_per_month.remaining_debt >= payment_sum:
                attendance_per_month.remaining_debt -= payment_sum
                attendance_per_month.payment += payment_sum
                payment_sum = 0
                if attendance_per_month.remaining_debt == 0:
                    attendance_per_month.status = True
            else:
                payment_sum -= attendance_per_month.remaining_debt
                attendance_per_month.payment += attendance_per_month.remaining_debt
                attendance_per_month.remaining_debt = 0
                attendance_per_month.status = True
            attendance_per_month.save()
        student_payment.extra_payment = payment_sum
        student_payment.save()
        total_debt = 0
        remaining_debt = 0
        attendance_per_months = AttendancePerMonth.objects.filter(student=validated_data.get('student'),
                                                                  status=False).all()
        for attendance_per_month in attendance_per_months:
            total_debt += attendance_per_month.total_debt
            remaining_debt += attendance_per_month.remaining_debt
        if remaining_debt == 0:
            student.debt_status = 0
        elif student.total_payment_month > total_debt:
            student.debt_status = 1
            TeacherBlackSalary.objects.filter(student=student, status=False).update(status=True)
        elif student.total_payment_month < total_debt:
            student.debt_status = 2
        student.save()
        return student_payment

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        instance.student.extra_payment -= instance.payment_sum
        instance.student.extra_payment.save()
        return instance


class StudentPaymentListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=True)
    payment_type = PaymentTypesSerializers(required=True)
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = StudentPayment
        fields = ['id', 'student', 'payment_type', 'payment_sum', 'status']


class DeletedNewStudentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = DeletedNewStudent
        fields = ['id', 'student']


class DeletedNewStudentListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = DeletedNewStudent
        fields = ['id', 'student']


class DeletedStudentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    group_reason = serializers.PrimaryKeyRelatedField(queryset=GroupReason.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False)

    class Meta:
        model = DeletedStudent
        fields = ['id', 'student', 'group', 'teacher', 'group_reason', 'branch']

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


class DeletedStudentListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=True)
    group = GroupSerializer(required=True)
    teacher = TeacherSerializer(required=True)
    group_reason = GroupReasonSerializers(required=True)

    class Meta:
        model = DeletedStudent
        fields = ['id', 'student', 'group', 'teacher', 'group_reason']
