from datetime import datetime

from django.db.models import Q
from rest_framework import serializers
from django.utils.timezone import now

from branch.models import Branch
from branch.serializers import BranchSerializer
from classes.models import ClassNumber, ClassColors
from gennis_platform.settings import classroom_server
from gennis_platform.uitils import request
from group.functions.CreateSchoolStudentDebts import create_school_student_debts
from group.models import Group, GroupReason, CourseTypes, GroupSubjects
from language.models import Language
from language.serializers import LanguageSerializers
from students.models import DeletedNewStudent
from students.models import Student, DeletedStudent, StudentHistoryGroups
from subjects.models import Subject, SubjectLevel
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from system.models import System
from system.serializers import SystemSerializers
from teachers.models import Teacher, TeacherHistoryGroups
from teachers.serializers import TeacherSerializer
from time_table.models import GroupTimeTable
import pprint


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
    group_reason = serializers.IntegerField(default=None, allow_null=True)
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
    delete_type = serializers.CharField(default=None, allow_blank=True)
    comment = serializers.CharField(default=None, allow_blank=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'deleted', 'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number',
                  'color', 'course_types', 'class_number', 'update_method', 'time_table', 'create_type', 'group_type',
                  'delete_type', 'comment', 'group_reason']

    def create(self, validated_data):
        time_tables = validated_data.pop('time_table', None)
        create_type = validated_data.pop('create_type')
        students_data = validated_data.pop('students', [])
        teacher_data = validated_data.pop('teacher', [])

        today = datetime.now()

        active_groups = Group.objects.filter(Q(deleted=False),
                                             system_id=validated_data.get('branch').location.system_id)
        group = Group.objects.create(**validated_data, system_id=validated_data.get('branch').location.system_id)

        for student in students_data:
            if not active_groups.filter(students__id=student.id).exists():
                group.students.set(students_data)
        group.teacher.set(teacher_data)
        for student in students_data:
            StudentHistoryGroups.objects.create(group=group, student=student, teacher=teacher_data[0],
                                                joined_day=today)
        TeacherHistoryGroups.objects.create(group=group, teacher=teacher_data[0], joined_day=today)
        create_school_student_debts(group, group.students.all())

        return group

    def update(self, instance, validated_data):
        group_type = validated_data.get('group_type')
        color = validated_data.get('color')
        update_method = validated_data.get("update_method")
        students = validated_data.get("students")
        delete_type = validated_data.get("delete_type")
        comment = validated_data.get("comment")
        group_reason = validated_data.get("group_reason")
        price = validated_data.pop("price", None)
        if price:
            instance.price = price
            instance.save()
            today = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            from attendances.models import AttendancePerMonth
            attendances = AttendancePerMonth.objects.filter(month_date__gte=today, group=instance)

            for attendance in attendances:
                attendance.total_debt = price
                attendance.save()
        teacher_status = True
        for attr, value in validated_data.items():
            if attr != 'update_method' and attr != 'students' and attr != 'teacher':
                setattr(instance, attr, value)

        if group_type == 'school':
            if 'teacher' in validated_data:
                teacher_history_group = TeacherHistoryGroups.objects.get(group=instance,
                                                                         teacher=instance.teacher.all()[0])
                teacher_history_group.left_day = datetime.now()
                teacher_history_group.save()
                teach = instance.teacher.all()[0]
                # request(url=f"{classroom_server}/delete_teacher_from_group/{teach.user_id}/{instance.id}/turon",
                #         method='DELETE')

                for time_table in instance.classtimetable_set.all():
                    instance.teacher.all()[0].class_time_table.remove(time_table)
                    validated_data.get('teacher')[0].class_time_table.add(time_table)
                instance.teacher.remove(instance.teacher.all()[0])
                instance.teacher.remove(*instance.teacher.all())
                instance.teacher.add(validated_data.get('teacher')[0])
                TeacherHistoryGroups.objects.create(group=instance, teacher=validated_data.get('teacher')[0],
                                                    joined_day=datetime.now())
            if update_method:
                if update_method == "add_students":
                    for student in students:
                        instance.students.add(student)
                        StudentHistoryGroups.objects.create(group=instance, student=student,
                                                            teacher=instance.teacher.all()[
                                                                0] if instance.teacher.all() else None,
                                                            joined_day=datetime.now())
                        if instance.classtimetable_set.all():
                            for time_table in instance.classtimetable_set.all():
                                student.class_time_table.add(time_table)
                    create_school_student_debts(instance, students)
                elif update_method == "remove_students":

                    if delete_type == 'new_students':
                        for student in students:
                            today = datetime.now()
                            date = datetime(today.year, today.month, 1)
                            month_date = date.strftime("%Y-%m-%d")
                            attendances_per_month = student.attendancepermonth_set.filter(group=instance,
                                                                                          student=student,
                                                                                          month_date__gte=month_date,
                                                                                          payment=0)
                            for attendance in attendances_per_month:
                                attendance.delete()
                            instance.students.remove(student)
                            student_history_group = StudentHistoryGroups.objects.get(group=instance,
                                                                                     teacher=instance.teacher.all()[
                                                                                         0] if instance.teacher.all() else None,
                                                                                     student=student)
                            student_history_group.left_day = datetime.now()
                            student_history_group.save()
                            if instance.classtimetable_set.all():
                                for time_table in instance.classtimetable_set.all():
                                    student.class_time_table.remove(time_table)
                    else:
                        for student in students:
                            today = datetime.now()
                            date = datetime(today.year, today.month, 1)
                            month_date = date.strftime("%Y-%m-%d")
                            attendances_per_month = student.attendancepermonth_set.filter(group=instance,
                                                                                          student=student,
                                                                                          month_date__gte=month_date,
                                                                                          payment=0)
                            for attendance in attendances_per_month:
                                attendance.delete()
                            attendances_per_month2 = student.attendancepermonth_set.filter(
                                student=student,
                                month_date__lte=month_date,
                                payment=0)
                            for attendance in attendances_per_month2:
                                if attendance.group == instance:
                                    attendance.delete()
                            instance.students.remove(student)
                            DeletedStudent.objects.create(student=student, group=instance,
                                                          comment=comment if comment else None,
                                                          group_reason_id=group_reason if group_reason else None)
                            student_history_group = StudentHistoryGroups.objects.get(group=instance,
                                                                                     teacher=instance.teacher.all()[
                                                                                         0] if instance.teacher.all() else None,
                                                                                     student=student)
                            student_history_group.left_day = datetime.now()
                            student_history_group.save()
                            if instance.classtimetable_set.all():
                                for time_table in instance.classtimetable_set.all():
                                    student.class_time_table.remove(time_table)
        instance.color = validated_data.get('color', instance.color)
        instance.save()
        from group.serializers_list.serializers_self import GroupListSerializer
        return GroupListSerializer(instance).data


class GroupSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()
    language = LanguageSerializers()
    level = SubjectLevelSerializer()
    subject = SubjectSerializer()
    teacher = TeacherSerializer(many=True)
    system = SystemSerializers()
    course_types = CourseTypesSerializers()
    students = serializers.SerializerMethodField()
    class_number = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number', 'color',
                  'course_types', 'deleted']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # 'fields' from context (passed from the view)
        fields = self.context.get('fields', None)
        # Filter fields based on 'fields' from context
        if fields:
            filtered_representation = {}

            # Function to handle any number of nested fields
            def set_nested_value(source_dict, target_dict, field_parts):
                """
                Recursively sets nested fields based on field_parts.
                This handles fields with arbitrary depth of nesting.
                """
                current_field = field_parts[0]
                if current_field in source_dict:
                    if len(field_parts) == 1:
                        # Base case: If we're at the last field part, set the value
                        target_dict[current_field] = source_dict[current_field]
                    else:
                        # Recursive case: Go deeper into the nested field
                        if current_field not in target_dict:
                            target_dict[current_field] = {}
                        set_nested_value(source_dict[current_field], target_dict[current_field], field_parts[1:])

            # Iterate over the fields and process each one
            for field in fields:
                field_parts = field.split('__')
                set_nested_value(representation, filtered_representation, field_parts)

            return filtered_representation

        return representation

    def get_students(self, obj):
        from students.serializers import StudentListSerializer
        return StudentListSerializer(obj.students.all(), many=True).data

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberListSerializers
        return ClassNumberListSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
        from lesson_plan.functions.utils import update_lesson_plan
        # update_lesson_plan(obj.id)
        return ClassColorsSerializers(obj.color).data


class GroupClassSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()
    language = LanguageSerializers()
    level = SubjectLevelSerializer()
    subject = SubjectSerializer()
    teacher = TeacherSerializer(many=True)
    system = SystemSerializers()
    course_types = CourseTypesSerializers()
    students = serializers.SerializerMethodField()
    class_number = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    type = serializers.CharField(default='group', read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number', 'color',
                  'course_types', 'type']

    def get_students(self, obj):
        from students.serializers import StudentListSerializer
        return StudentListSerializer(obj.students.all(), many=True).data

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberListSerializers
        return ClassNumberListSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
        return ClassColorsSerializers(obj.color).data

    def get_name(self, obj):
        class_number = self.get_class_number(obj)
        color = self.get_color(obj)
        return f"{class_number['number']} - {color['name']}"


class GroupSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(many=True)
    group = serializers.SerializerMethodField()
    class_type = serializers.SerializerMethodField()

    class Meta:
        model = GroupSubjects
        fields = ['id', 'subject', 'hours', 'group', 'class_type']

    def get_group(self, obj):
        return {
            'id': obj.group_subjects.id,
            'name': obj.group_subjects.color.name,
            "class_number": obj.group_subjects.class_number.number
        }

    def get_class_type(self, obj):
        return {
            'id': obj.class_type.id,
            'name': obj.class_type.name
        }


class GroupListSerializer(serializers.ModelSerializer):
    class_number = serializers.CharField(required=False, source='class_number.number')
    color = serializers.CharField(required=False, source='color.name')
    subjects = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Group
        fields = ['id', "class_number", "color", 'price', 'subjects']

    def get_subjects(self, obj):
        data = []
        group_subjects = GroupSubjects.objects.filter(group=obj).order_by("pk").all()
        for subject in group_subjects:
            info = {
                "subject_name": subject.subject.name,
                "subject_id": subject.subject.pk,
                "hours": subject.hours,
                "from_database": True
            }
            data.append(info)
        return data
