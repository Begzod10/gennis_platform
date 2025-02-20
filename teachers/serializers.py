import pprint

from rest_framework import serializers
from teachers.functions.school.CalculateTeacherSalary import calculate_teacher_salary
from branch.models import Branch
from branch.serializers import BranchSerializer
from classes.models import ClassTypes
from flows.models import Flow
from group.models import Group
from language.models import Language
from language.serializers import LanguageSerializers
from payments.models import PaymentTypes
from payments.serializers import PaymentTypesSerializers
from subjects.serializers import Subject
from subjects.serializers import SubjectLevelSerializer, SubjectSerializer
from system.models import System
from system.serializers import SystemSerializers
from teachers.models import TeacherGroupStatistics, Teacher
from user.serializers import UserSerializerWrite, UserSerializerRead
from .models import (TeacherAttendance)
from .models import (TeacherSalaryList, TeacherSalary, TeacherSalaryType)


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializerWrite()
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)
    teacher_salary_type = serializers.PrimaryKeyRelatedField(queryset=TeacherSalaryType.objects.all(), required=False,
                                                             allow_null=True)
    class_type = serializers.PrimaryKeyRelatedField(queryset=ClassTypes.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Teacher
        fields = ['user', 'subject', 'color', 'total_students', 'id', 'teacher_salary_type', 'salary_percentage',
                  'class_type', 'working_hours', 'class_salary']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['subject'] = [{
            'id': subject.id,
            'name': subject.name
        } for subject in instance.subject.all()]

        return representation

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
        for subject in subject_data:
            teacher.subject.add(subject)
        branch = Branch.objects.get(pk=user_data['branch'])
        teacher.branches.add(branch)
        return teacher

    def update(self, instance, validated_data):
        calculate_teacher_salary(instance)
        user_data = validated_data.pop('user', None)
        subject_data = validated_data.pop('subject')

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()
        instance.subject.clear()
        subjects_info = []
        for subject in subject_data:
            instance.subject.add(subject)
            subjects_info.append({
                'id': subject.id,
                'name': subject.name
            })

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TeacherAttendanceSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all())
    day = serializers.DateField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = TeacherAttendance
        fields = ['id', 'teacher', 'system', 'day', 'status']


class TeacherAttendanceListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    teacher = TeacherSerializer(required=False)
    system = SystemSerializers(required=False)
    day = serializers.DateField(required=False)
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


class GroupSerializerTeachers(serializers.ModelSerializer):
    branch = BranchSerializer()
    language = LanguageSerializers()
    level = SubjectLevelSerializer()
    subject = SubjectSerializer()
    system = SystemSerializers()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'teacher', 'system', 'class_number', 'color',
                  'course_types']

    @property
    def course_types(self):
        from group.serializers import CourseTypesSerializers
        return CourseTypesSerializers()

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberSerializers
        return ClassNumberSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
        return ClassColorsSerializers(obj.color).data


class TeacherSerializerRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    subject = SubjectSerializer(many=True)
    teacher_salary_type = TeacherSalaryTypeSerializerRead(read_only=True)
    group = GroupSerializerTeachers(many=True, source='group_set')
    calculate = serializers.SerializerMethodField(read_only=True, required=False, allow_null=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = "__all__"

    def get_calculate(self, obj):
        from .functions.school.CalculateTeacherSalary import calculate_teacher_salary
        calculate_teacher_salary(obj)

    def get_status(self, obj):
        flows = Flow.objects.filter(teacher=obj).exists()
        group = Group.objects.filter(teacher=obj).exists()
        if flows or group:
            return False
        else:
            return True


class TeacherSalaryReadSerializers(serializers.ModelSerializer):
    from group.serializers import BranchSerializer
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


class TeacherSalaryCreateSerializersUpdate(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    teacher_salary_type = serializers.PrimaryKeyRelatedField(queryset=TeacherSalaryType.objects.all(), required=False,
                                                             allow_null=True)
    worked_hours = serializers.IntegerField(required=False, allow_null=True)
    salary_type = serializers.BooleanField(required=False)

    class Meta:
        model = TeacherSalary
        fields = '__all__'

    def update(self, instance, validated_data):
        salary = super().update(instance, validated_data)
        pprint.pprint(validated_data)
        type_salary = validated_data.get('salary_type', None)
        from .functions.school.CalculateTeacherSalary import teacher_salary_school
        if instance.teacher.user.branch.location.system.name == 'school':
            if type_salary:
                worked_hours = validated_data.get('worked_hours', None)
                teacher_salary_school(salary_id=instance.id, worked_hours=worked_hours, class_salary=0,
                                      type_salary=type_salary)
            else:
                class_salary = validated_data.get('class_salary', None)
                teacher_salary_school(salary_id=instance.id, worked_hours=0, class_salary=class_salary)

        return salary


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
        from .functions.school.CalculateTeacherSalary import calculate_teacher_salary
        if obj.teacher.user.branch.location.system.name == 'school':
            calculate_teacher_salary(obj.teacher)
        return obj.date.strftime('%Y-%m-%d %H:%M')


class TeacherSalaryListCreateSerializers(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    salary_id = serializers.PrimaryKeyRelatedField(queryset=TeacherSalary.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    name = serializers.SerializerMethodField(required=False, read_only=True)
    surname = serializers.SerializerMethodField(required=False, read_only=True)
    date = serializers.DateField(input_formats=["%Y-%m-%d"], required=True)
    payment_type_name = serializers.SerializerMethodField(required=False, read_only=True)
    comment = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = TeacherSalaryList
        fields = '__all__'

    def get_name(self, obj):
        return obj.teacher.user.name

    def get_surname(self, obj):
        return obj.teacher.user.surname

    def get_payment_type_name(self, obj):
        return obj.payment.name

    def create(self, validated_data):
        teacher = validated_data.get('teacher')
        salary_id = validated_data.get('salary_id')
        salary_amount = validated_data.get('salary')
        date = validated_data.get('date')

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
            date=date,
            deleted=False,
            comment=validated_data.get('comment', ''),
        )
        return teacher_salary_list

    def update(self, instance, validated_data):
        salary_id = validated_data.get('salary_id', instance.salary_id)
        salary_amount = validated_data.get('salary', instance.salary)
        date = validated_data.get('date', instance.date)  # Sana yangilanadi

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
        instance.date = date
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance
