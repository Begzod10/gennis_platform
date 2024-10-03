from datetime import datetime

from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from classes.models import ClassNumber, ClassColors
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
from .functions.CreateSchoolStudentDebts import create_school_student_debts
from .models import Group, GroupReason, CourseTypes


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

        if create_type == 'school':
            group = Group.objects.create(**validated_data, system_id=validated_data.get('branch').location.system_id)
            group.students.set(students_data)
            group.teacher.set(teacher_data)
            for student in students_data:
                StudentHistoryGroups.objects.create(group=group, student=student, teacher=teacher_data[0],
                                                    joined_day=today)
            TeacherHistoryGroups.objects.create(group=group, teacher=teacher_data[0], joined_day=today)
            create_school_student_debts(group, group.students.all())
        else:
            group = Group.objects.create(**validated_data, system_id=validated_data.get('branch').location.system_id)
            group.students.set(students_data)
            group.teacher.set(teacher_data)
            for student in students_data:
                StudentHistoryGroups.objects.create(group=group, student=student, teacher=teacher_data[0],
                                                    joined_day=today)
            TeacherHistoryGroups.objects.create(group=group, teacher=teacher_data[0], joined_day=today)
            subject = validated_data.get('subject')
            teacher_subjects = Teacher.objects.filter(id=teacher_data[0].id, subject__in=[subject.id]).first()
            if not teacher_subjects:
                raise serializers.ValidationError('Ustozni fani togri kelmadi')

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
        group_type = validated_data.get('group_type')
        update_method = validated_data.get("update_method")
        students = validated_data.get("students")
        delete_type = validated_data.get("delete_type")
        comment = validated_data.get("comment")
        group_reason = validated_data.get("group_reason")
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
                                                            teacher=instance.teacher.all()[0],
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
                            DeletedNewStudent.objects.create(student=student, comment=comment)
                            student_history_group = StudentHistoryGroups.objects.get(group=instance,
                                                                                     teacher=instance.teacher.all()[0],
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
                                                                                     teacher=instance.teacher.all()[0],
                                                                                     student=student)
                            student_history_group.left_day = datetime.now()
                            student_history_group.save()
                            if instance.classtimetable_set.all():
                                for time_table in instance.classtimetable_set.all():
                                    student.class_time_table.remove(time_table)
        else:
            if 'teacher' in validated_data:
                teacher_history_group = TeacherHistoryGroups.objects.get(group=instance,
                                                                         teacher=instance.teacher.all()[0])
                teacher_history_group.left_day = datetime.now()
                teacher_history_group.save()
                for time_table in instance.group_time_table.all():
                    instance.teacher.all()[0].group_time_table.remove(time_table)
                    validated_data.get('teacher')[0].group_time_table.add(time_table)
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
                                                            teacher=instance.teacher.all()[0],
                                                            joined_day=datetime.now())
                        if instance.group_time_table.all():
                            for time_table in instance.group_time_table.all():
                                student.group_time_table.add(time_table)
                elif update_method == "remove_students":
                    if delete_type == 'new_students':
                        for student in students:
                            instance.students.remove(student)
                            DeletedNewStudent.objects.create(student=student, comment=comment)
                            if instance.group_time_table.all():
                                for time_table in instance.group_time_table.all():
                                    student.group_time_table.remove(time_table)
                    else:
                        for student in students:
                            instance.students.remove(student)
                            DeletedStudent.objects.create(student=student, group=instance,
                                                          comment=comment if comment else None,
                                                          group_reason_id=group_reason if group_reason else None)
                            if instance.group_time_table.all():
                                for time_table in instance.group_time_table.all():
                                    student.group_time_table.remove(time_table)
                    student_history_group = StudentHistoryGroups.objects.get(group=instance,
                                                                             teacher=instance.teacher.all()[0])
                    student_history_group.left_day = datetime.now()
                    student_history_group.save()
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
    class_number = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number', 'color',
                  'course_types', 'deleted']

    def get_students(self, obj):
        from students.serializers import StudentListSerializer
        return StudentListSerializer(obj.students.all(), many=True).data

    def get_class_number(self, obj):
        from classes.serializers import ClassNumberListSerializers
        return ClassNumberListSerializers(obj.class_number).data

    def get_color(self, obj):
        from classes.serializers import ClassColorsSerializers
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
