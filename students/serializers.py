from datetime import date

from django.db.models import Sum
from rest_framework import serializers
from pprint import pprint
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


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializerWrite()
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True, required=False)
    parents_number = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    shift = serializers.CharField()
    class_number = serializers.PrimaryKeyRelatedField(queryset=ClassNumber.objects.all())
    face_id = serializers.CharField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Student
        fields = '__all__'

    def to_internal_value(self, data):
        """Override to remove username if it hasn't changed BEFORE validation"""
        if self.instance and 'user' in data and 'username' in data['user']:
            if data['user']['username'] == self.instance.user.username:
                # Create a mutable copy and remove username
                import copy
                data = copy.deepcopy(data)
                data['user'].pop('username')

        return super().to_internal_value(data)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subject_data = validated_data.pop('subject', [])

        if isinstance(user_data.get('language'), Language):
            user_data['language'] = user_data['language'].id
        if isinstance(user_data.get('branch'), Branch):
            user_data['branch'] = user_data['branch'].id

        user_serializer = UserSerializerWrite(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        student = Student.objects.create(user=user, **validated_data)

        if subject_data:
            student.subject.set(subject_data)

        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        subject_data = validated_data.pop('subject', None)
        face_id = validated_data.pop('face_id', None)

        if user_data:
            if isinstance(user_data.get('language'), Language):
                user_data['language'] = user_data['language'].id

            if isinstance(user_data.get('branch'), Branch):
                user_data['branch'] = user_data['branch'].id

            user_serializer = UserSerializerWrite(
                instance=instance.user,
                data=user_data,
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        if face_id is not None:
            instance.user.face_id = face_id
            instance.user.save(update_fields=['face_id'])

        if subject_data is not None:
            instance.subject.set(subject_data)

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
    name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'teacher', 'system', 'class_number', 'color',
                  'course_types']

    def get_name(self, obj):
        if obj.name:
            return obj.name
        else:
            return f"{obj.class_number.number}-{obj.color.name}"

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberSerializers
        return ClassNumberSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
        return ClassColorsSerializers(obj.color).data


def get_remaining_debt_for_student(student_id):
    student = Student.objects.get(pk=student_id)
    group = student.groups_student.first()
    if group:
        attendances = AttendancePerMonth.objects.filter(student_id=student_id, group_id=group.id).all()
        current_date = date.today()
        for month in attendances:
            if month.payment == 0 and month.remaining_debt == 0:
                month.remaining_debt = month.total_debt
                month.save()
            if month.payment < 0:
                month.payment = 0
                month.save()
            if month.total_debt:
                month.remaining_debt = max(0, month.total_debt - (month.payment + month.discount))
                month.save()

        remaining_debt_sum = AttendancePerMonth.objects.filter(
            student_id=student_id,
            group_id=group.id,
            month_date__lte=current_date
        ).aggregate(total_remaining_debt=Sum('remaining_debt'))
        total_remaining_debt = remaining_debt_sum['total_remaining_debt'] or 0

        if total_remaining_debt == 0:
            remaining_debt_sum = AttendancePerMonth.objects.filter(
                student_id=student_id,
                group_id=group.id,
                month_date__gte=current_date
            ).aggregate(total_remaining_debt=Sum('payment'))
            student.user.balance = remaining_debt_sum['total_remaining_debt']
            student.user.save()

            return remaining_debt_sum['total_remaining_debt'] or 0
        else:
            student.user.balance = f"-{total_remaining_debt}"
            student.user.save()

            return f"-{total_remaining_debt}"


class StudentListSerializer(serializers.ModelSerializer):
    from classes.serializers import ClassNumberSerializers
    user = UserSerializerRead(required=False)
    subject = SubjectSerializer(many=True, required=False)
    parents_number = serializers.CharField()
    shift = serializers.CharField()
    group = serializers.SerializerMethodField(required=False)
    contract = serializers.SerializerMethodField(required=False)
    color = serializers.SerializerMethodField(required=False)
    debt = serializers.SerializerMethodField(required=False)
    class_number = ClassNumberSerializers()
    face_id = serializers.CharField(source='user.face_id', read_only=True)

    class Meta:
        model = Student
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        fields = self.context.get('fields', None)

        if fields:
            filtered_representation = {}
            for field in fields:
                field_parts = field.split('__')

                def set_nested_value(source_dict, target_dict, field_parts):
                    current_field = field_parts[0]
                    if current_field in source_dict:
                        if type(source_dict[current_field]) == list:
                            for item in source_dict[current_field]:
                                if len(field_parts) == 1:
                                    target_dict[current_field] = item
                                else:
                                    if current_field not in target_dict:
                                        target_dict[current_field] = {}
                                    set_nested_value(item, target_dict[current_field], field_parts[1:])


                        else:

                            if len(field_parts) == 1:
                                target_dict[current_field] = source_dict[current_field]
                            else:
                                if current_field not in target_dict:
                                    target_dict[current_field] = {}
                                set_nested_value(source_dict[current_field], target_dict[current_field],
                                                 field_parts[1:])

                set_nested_value(representation, filtered_representation, field_parts)

            return filtered_representation

        return representation

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
        debt = 0
        if obj.user.branch.location.system.name == 'school':
            debt = get_remaining_debt_for_student(obj.id)
        else:
            groups = obj.groups_student.all()
            for group in groups:
                for i in group.teacher.all():
                    for salary in i.teacher_black_salary.filter(student_id=obj.id).all():
                        debt += salary.black_salary if salary.black_salary else 0

        return debt

    def get_contract(self, obj):
        contracts = obj.contract_student_id.all()
        if contracts.exists():
            contract_list = [{"url": contract.contract.url if contract.contract else None} for contract in contracts]
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


class StudentHistoryGroupsListSerializer2(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    reason = serializers.CharField(required=False)

    class Meta:
        model = StudentHistoryGroups
        fields = [
            'id',
            'student',
            'group',
            'teacher',
            'reason',
            'joined_day',
            'left_day',
        ]

    def get_student(self, obj):
        student = getattr(obj, 'student', None)
        if not student:
            return None
        user = getattr(student, 'user', None)
        return {
            "id": student.id,
            "name": getattr(user, 'name', None),
            "surname": getattr(user, 'surname', None)
        }

    def get_group(self, obj):
        group = getattr(obj, 'group', None)
        if not group:
            return None
        return {
            "id": group.id,
            "name": group.name,
            "price": group.price
        }

    def get_teacher(self, obj):
        teacher = getattr(obj, 'teacher', None)
        if not teacher:
            return None
        user = getattr(teacher, 'user', None)
        return {
            "id": teacher.id,
            "name": getattr(user, 'name', None),
            "surname": getattr(user, 'surname', None)
        }


class StudentCharitySerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    charity_sum = serializers.IntegerField(required=False)

    class Meta:
        model = StudentCharity
        fields = ['id', 'student', 'group', 'charity_sum', 'name']


class StudentCharityListSerializer(serializers.ModelSerializer):
    # student = StudentSerializer(required=True)
    # group = GroupSerializer(required=True)
    charity_sum = serializers.IntegerField(required=False)

    class Meta:
        model = StudentCharity
        fields = ['id', 'charity_sum', 'name']


class StudentPaymentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)
    name = serializers.SerializerMethodField(required=False, read_only=True)
    surname = serializers.SerializerMethodField(required=False, read_only=True)
    payment_type_name = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = StudentPayment
        fields = ['student', 'payment_type', 'payment_sum', 'status', 'branch', 'name', 'surname', 'added_data',
                  'payment_type_name', 'date']

    def get_name(self, obj):
        return obj.student.user.name

    def get_surname(self, obj):
        return obj.student.user.surname

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
    payment_type = serializers.SerializerMethodField(required=False)
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False, source='deleted')
    attendance =serializers.SerializerMethodField()

    class Meta:
        model = StudentPayment
        fields = ['id', 'student', 'payment_type', 'payment_sum', 'status', 'added_data', 'date','attendance']

    def get_payment_type(self, obj):
        info = {
            'id': obj.payment_type.id,
            'name': "skidka" if obj.status == True else obj.payment_type.name
        }
        return info

    def get_attendance(self, obj):
        """return month name"""
        return obj.attendance.month_date.strftime("%B") if obj.attendance else ""


class DeletedNewStudentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = DeletedNewStudent
        fields = ['id', 'student']


class StudentSerializerLists(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    group = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Student
        fields = ['id', 'user', 'group']

    def get_group(self, obj):
        return [GroupSerializerStudents(group).data for group in obj.groups_student.all()]


class DeletedNewStudentListSerializer(serializers.ModelSerializer):
    student = StudentSerializerLists(read_only=True)

    class Meta:
        model = DeletedNewStudent
        fields = ['id', 'student']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {'id': representation['student']['id'], 'user': representation['student']['user'],
                'class': representation['student']['group'], "deleted": True, 'date': instance.created,
                'comment': instance.comment}


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
            deleted_students_number = len(
                DeletedStudent.objects.get(teacher=validated_data.get('teacher'), deleted=False).all()) / 100

            number_students = len(DeletedStudent.objects.get(reason=validated_data.get('group_reason'),
                                                             teacher=validated_data.get('teacher'),
                                                             deleted=False).all())
            percentage = deleted_students_number * number_students
            teacher_group_statistics.number_students = number_students
            teacher_group_statistics.percentage = percentage
            teacher_group_statistics.save()
        else:
            deleted_students_number = len(
                DeletedStudent.objects.get(teacher=validated_data.get('teacher'), deleted=False).all()) / 100

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
        fields = ['id', 'student', 'group', 'teacher', 'group_reason', 'deleted_date', 'comment']


class StudentClassNumberSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Student
        fields = ['class_number', 'students']

    def update(self, instance, validated_data):
        students = validated_data.pop('students', None)
        for student in students:
            get_student = Student.objects.get(id=student)
            get_student.class_number = instance
            get_student.save()

        return {"msg": "O'quvchilar sinf raqami o'zgartirildi"}
