from rest_framework import serializers

from branch.models import Branch
from language.models import Language
from students.models import StudentHistoryGroups, Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher, TeacherHistoryGroups
from time_table.models import WeekDays
from .models import Group, GroupReason, CourseTypes
from classes.models import ClassNumber, ClassColors

from branch.serializers import BranchSerializer
from language.serializers import LanguageSerializers
from students.serializers import StudentSerializer
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from system.serializers import SystemSerializers
from teachers.serializers import TeacherSerializer


class CourseTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = CourseTypes
        fields = '__all__'


class GroupReasonSerializers(serializers.ModelSerializer):
    class Meta:
        model = GroupReason
        fields = '__all__'


class GroupCreateUpdateSerializer(serializers.ModelSerializer):
    week = serializers.PrimaryKeyRelatedField(queryset=WeekDays.objects.all(), default=None, allow_blank=True)
    update_method = serializers.CharField(default=None, allow_blank=True)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())
    level = serializers.PrimaryKeyRelatedField(queryset=SubjectLevel.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), many=True)
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all())
    class_number = serializers.PrimaryKeyRelatedField(queryset=ClassNumber.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=ClassColors.objects.all())
    course_types = serializers.PrimaryKeyRelatedField(queryset=CourseTypes.objects.all(), required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'deleted', 'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number',
                  'color', 'course_types', 'class_number', 'update_method', 'week']

    def create(self, validated_data):
        students = validated_data.get('students')
        week = validated_data.get('week')

        print(week)
        group = Group.objects.create(**validated_data)
        # for student in students:
        #     tatus = True
        #     for st_group in student.groups_student.all():
        #         if instance.group_time_table.start_time == st_group.group_time_table.start_time and instance.group_time_table.week == st_group.group_time_table.week and instance.group_time_table.room == st_group.group_time_table.room and instance.group_time_table.end_time == st_group.group_time_table.end_time:
        #             status = False
        #             break
        group.save()
        return group

    def update(self, instance, validated_data):
        update_method = validated_data.get("update_method")
        students = validated_data.get("students")

        for attr, value in validated_data.items():
            if attr != 'update_method' and attr != 'students' and attr != 'teacher':
                setattr(instance, attr, value)

        if 'teacher' in validated_data:
            instance.teacher.remove(*instance.teacher.all())
            instance.teacher.set(validated_data['teacher'])

        if update_method:
            if update_method == "add_students":
                for student in students:
                    status = True
                    for st_group in student.groups_student.all():
                        if instance.group_time_table.start_time == st_group.group_time_table.start_time and instance.group_time_table.week == st_group.group_time_table.week and instance.group_time_table.room == st_group.group_time_table.room and instance.group_time_table.end_time == st_group.group_time_table.end_time:
                            status = False
                            break
                    if status:
                        instance.students.add(student)
            elif update_method == "remove_students":
                for student in students:
                    instance.students.remove(student)

        instance.save()
        return instance


class GroupSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()
    language = LanguageSerializers()
    level = SubjectLevelSerializer()
    subject = SubjectSerializer()
    students = StudentSerializer(many=True)
    teacher = TeacherSerializer(many=True)
    system = SystemSerializers()
    course_types = CourseTypesSerializers()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number', 'color',
                  'course_types']

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberSerializers
        return ClassNumberSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
        return ClassColorsSerializers(obj.color).data
