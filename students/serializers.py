from rest_framework import serializers

from attendances.models import AttendancePerMonth
from branch.models import Branch
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


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializerWrite()
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)
    parents_number = serializers.CharField()
    shift = serializers.CharField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'subject', 'parents_number', 'shift']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        if isinstance(user_data.get('language'), Language):
            user_data['language'] = user_data['language'].id
        if isinstance(user_data.get('branch'), Branch):
            user_data['branch'] = user_data['branch'].id
        subject_data = validated_data.pop('subject')

        user_serializer = UserSerializerWrite(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        student = Student.objects.create(user=user, parents_number=validated_data.get('parents_number'),
                                         shift=validated_data.get('shift'))
        student.subject.set(subject_data)
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


class GroupSerializerStudents(serializers.ModelSerializer):
    branch = BranchSerializer()
    language = LanguageSerializers()
    level = SubjectLevelSerializer()
    subject = SubjectSerializer()
    teacher = TeacherSerializerRead(many=True)
    system = SystemSerializers()
    course_types = CourseTypesSerializers()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'teacher', 'system', 'class_number', 'color',
                  'course_types']

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberSerializers
        return ClassNumberSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
        return ClassColorsSerializers(obj.color).data


class StudentListSerializer(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    subject = SubjectSerializer(many=True)
    parents_number = serializers.CharField()
    shift = serializers.CharField()
    group = serializers.SerializerMethodField(required=False)
    contract = serializers.SerializerMethodField(required=False)
    color = serializers.SerializerMethodField(required=False)
    debt = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Student
        fields = '__all__'

    def get_group(self, obj):
        return [GroupSerializerStudents(group).data for group in obj.groups_student.all()]

    def get_color(self, obj):
        color = ''
        if obj.debt_status == 1:
            color = '#FACC15'
        elif obj.debt_status == 2:
            color = '#FF3130'
        elif obj.debt_status == 0:
            color = '24FF00'
        return color

    def get_debt(self, obj):
        groups = obj.groups_student.all()
        debt = 0
        for group in groups:
            for i in group.teacher.all():
                for salary in i.teacher_black_salary.filter(student_id=obj.id).all():
                    debt += salary.black_salary if salary.black_salary else 0

        return debt

    def get_contract(self, obj):
        contracts = obj.contract_student_id.all()
        if contracts.exists():
            contract_list = [{"url": contract.contract.url} for contract in contracts]
        else:
            contract_list = []
        return contract_list


class StudentHistoryGroupsSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    reason = serializers.CharField(required=False)
    joined_day = serializers.DateField(required=False)
    left_day = serializers.DateField(required=False)

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

    class Meta:
        model = StudentHistoryGroups
        fields = ['id', 'student', 'group', 'teacher', 'reason', 'joined_day', 'left_day']


class StudentCharitySerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    charity_sum = serializers.IntegerField(required=False)

    class Meta:
        model = StudentCharity
        fields = ['id', 'student', 'group', 'charity_sum', 'name']


class StudentCharityListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=True)
    group = GroupSerializer(required=True)
    charity_sum = serializers.IntegerField(required=False)

    class Meta:
        model = StudentCharity
        fields = ['id', 'student', 'group', 'charity_sum', 'name']


class StudentPaymentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)
    name = serializers.SerializerMethodField(required=False, read_only=True)
    surname = serializers.SerializerMethodField(required=False, read_only=True)
    date = serializers.SerializerMethodField(required=False, read_only=True)
    payment_type_name = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = StudentPayment
        fields = ['student', 'payment_type', 'payment_sum', 'status', 'branch', 'name', 'surname', 'date',
                  'payment_type_name']

    def get_name(self, obj):
        return obj.student.user.name

    def get_surname(self, obj):
        return obj.student.user.surname

    def get_date(self, obj):
        return obj.added_data.strftime('%Y-%m-%d')

    def get_payment_type_name(self, obj):
        return obj.payment_type.name

    def create(self, validated_data):
        attendance_per_months = AttendancePerMonth.objects.filter(student=validated_data.get('student'), status=False)
        student = Student.objects.get(pk=validated_data.get('student').id)
        student_payment = StudentPayment.objects.create(**validated_data)
        if student_payment.extra_payment:
            payment_sum = student_payment.payment_sum + student_payment.extra_payment
        else:
            payment_sum = 0

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
        attendance_per_months = AttendancePerMonth.objects.filter(student=validated_data.get('student'), status=False)

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


class StudentPaymentListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=True)
    payment_type = PaymentTypesSerializers(required=True)
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)
    added_data = serializers.SerializerMethodField(required=False)

    class Meta:
        model = StudentPayment
        fields = ['id', 'student', 'payment_type', 'payment_sum', 'status', 'added_data']

    def get_added_data(self, obj):
        return obj.added_data.strftime('%Y-%m-%d')





class DeletedNewStudentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = DeletedNewStudent
        fields = ['id', 'student']


class DeletedNewStudentListSerializer(serializers.ModelSerializer):
    student = StudentListSerializer(read_only=True)

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
    student = StudentListSerializer(required=True)
    group = GroupSerializer(required=True)
    teacher = TeacherSerializer(required=True)
    group_reason = GroupReasonSerializers(required=True)

    class Meta:
        model = DeletedStudent
        fields = ['id', 'student', 'group', 'teacher', 'group_reason']
