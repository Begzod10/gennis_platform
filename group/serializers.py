import pprint

from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher
from .models import Group, GroupReason, CourseTypes
from classes.models import ClassNumber, ClassColors
from time_table.models import GroupTimeTable
from branch.serializers import BranchSerializer
from language.serializers import LanguageSerializers
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from system.serializers import SystemSerializers
from teachers.serializers import TeacherSerializer

from .functions.checkTimeTable import check_time_table
from .functions.CreateSchoolStudentDebts import create_school_student_debts


class CourseTypesSerializers(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = CourseTypes
        fields = '__all__'


class GroupReasonSerializers(serializers.ModelSerializer):
    class Meta:
        model = GroupReason
        fields = '__all__'


class GroupCreateUpdateSerializer(serializers.ModelSerializer):
    group_type = serializers.CharField(default=None, allow_blank=True)
    time_table = serializers.JSONField(required=False, default=None)
    update_method = serializers.CharField(default=None, allow_blank=True)
    create_type = serializers.CharField(default=None, allow_blank=True)
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
                  'color', 'course_types', 'class_number', 'update_method', 'time_table', 'create_type', 'group_type']

    def create(self, validated_data):
        time_tables = validated_data.get('time_table')
        create_type = validated_data.pop('create_type')
        students_data = validated_data.pop('students', [])
        teacher_data = validated_data.pop('teacher', [])
        group = Group.objects.create(**validated_data, system_id=validated_data.get('branch').location.system_id)
        group.students.set(students_data)
        group.teacher.set(teacher_data)
        if create_type == 'school':
            create_school_student_debts(group, group.students.all())
        else:
            for time_table in time_tables:
                group_time_table = GroupTimeTable.objects.create(week_id=time_table['week'],
                                                                 start_time=time_table['start_time'],
                                                                 end_time=time_table['end_time'],
                                                                 room_id=time_table['room'], group=group,
                                                                 branch_id=time_table['branch'])
                for student in group.students.all():
                    student.group_time_table.add(group_time_table)
                for teacher in group.teacher.all():
                    teacher.group_time_table.add(group_time_table)
        return group

    def update(self, instance, validated_data):
        group_type = validated_data.pop('group_type')
        update_method = validated_data.get("update_method")
        students = validated_data.get("students")

        for attr, value in validated_data.items():
            if attr != 'update_method' and attr != 'students' and attr != 'teacher':
                setattr(instance, attr, value)

        if 'teacher' in validated_data:
            instance.teacher.remove(*instance.teacher.all())
            instance.teacher.set(validated_data['teacher'])
        if group_type == 'school':
            if update_method:
                if update_method == "add_students":
                    for student in students:
                        status = True
                        for flow in student.flow_set.all():
                            # if flow.classtimetable_set.filter()

                            status = False
                            break
                        if status:
                            instance.students.add(student)
                            create_school_student_debts(instance, instance.students.all())
                elif update_method == "remove_students":
                    for student in students:
                        instance.students.remove(student)
        else:
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
                            create_school_student_debts(instance, instance.students.all())
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
    teacher = TeacherSerializer(many=True)
    system = SystemSerializers()
    course_types = CourseTypesSerializers()
    students = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number', 'color',
                  'course_types']

    def get_students(self, obj):
        from students.serializers import StudentListSerializer
        return StudentListSerializer(obj.students.all(), many=True).data

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberSerializers
        return ClassNumberSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
        return ClassColorsSerializers(obj.color).data
