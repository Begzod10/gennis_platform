from rest_framework import serializers

from group.models import Group
from group.serializers import GroupSerializer
from students.serializers import Student, StudentSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from .models import LessonPlan, LessonPlanStudents


class LessonPlanSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = LessonPlan
        fields = ['teacher', 'group', 'date']


class LessonPlanGetSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    students =serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = '__all__'
    def get_students(self, obj):
        data =[]
        for i in obj.group.students.all():
            comment = LessonPlanStudents.objects.filter(lesson_plan_id=obj.id, student_id=i.id).first()
            data.append({
                "comment": comment.comment if comment else "",
                "student": {
                    "id": i.id,
                    "name": i.user.name,
                    "surname": i.user.surname
                }

            })
        return data


class LessonPlanStudentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lesson_plan = serializers.PrimaryKeyRelatedField(queryset=LessonPlan.objects.all())

    class Meta:
        model = LessonPlanStudents
        fields = ['comment', 'comment', 'student']


class LessonPlanStudentGetSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    lesson_plan = LessonPlanGetSerializer(read_only=True)

    class Meta:
        model = LessonPlanStudents
        fields = ['comment', 'comment', 'student']


class TeacherLessonPlanRangeSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    flow = serializers.SerializerMethodField()
    class_time_table = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = '__all__'

    def get_teacher(self, obj):
        if not obj.teacher:
            return None
        return {
            "id": obj.teacher.id,
            "name": obj.teacher.user.name if obj.teacher.user else "",
            "surname": obj.teacher.user.surname if obj.teacher.user else "",
            "phone": obj.teacher.user.phone if obj.teacher.user else ""
        }

    def get_group(self, obj):
        if not obj.group:
            return None
        return {
            "id": obj.group.id,
            "name": obj.group.name
        }

    def get_flow(self, obj):
        if not obj.flow:
            return None
        return {
            "id": obj.flow.id,
            "name": obj.flow.name
        }

    def get_class_time_table(self, obj):
        if not obj.class_time_table:
            return None
        ctt = obj.class_time_table
        return {
            "id": ctt.id,
            "name": ctt.name,
            "week": ctt.week.name_en if ctt.week else "",
            "hours": {
                "id": ctt.hours.id if ctt.hours else None,
                "name": ctt.hours.name if ctt.hours else "",
                "start_time": ctt.hours.start_time.strftime('%H:%M') if ctt.hours and ctt.hours.start_time else "",
                "end_time": ctt.hours.end_time.strftime('%H:%M') if ctt.hours and ctt.hours.end_time else ""
            } if ctt.hours else None,
            "room": {
                "id": ctt.room.id if ctt.room else None,
                "name": ctt.room.name if ctt.room else ""
            } if ctt.room else None,
            "subject": {
                "id": ctt.subject.id if ctt.subject else None,
                "name": ctt.subject.name if ctt.subject else ""
            } if ctt.subject else None
        }

    def get_students(self, obj):
        data = []
        students = []
        if obj.group:
            students = obj.group.students.all()
        elif obj.flow:
            students = obj.flow.students.all()
        
        for i in students:
            comment = LessonPlanStudents.objects.filter(lesson_plan_id=obj.id, student_id=i.id).first()
            data.append({
                "comment": comment.comment if comment else "",
                "student": {
                    "id": i.id,
                    "name": i.user.name if i.user else "",
                    "surname": i.user.surname if i.user else ""
                }
            })
        return data
