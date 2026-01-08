from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils.timezone import localtime
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from attendances.models import AttendancePerDay
from group.serializers import GroupCreateUpdateSerializer
from lesson_plan.models import LessonPlan, LessonPlanStudents
from teachers.models import TeacherSalary, Teacher
from user.models import CustomUser
from ..get_user import get_user




class TeacherTodayAttendanceSerializer(serializers.Serializer):
    group = serializers.CharField(allow_null=True)
    flow = serializers.CharField(allow_null=True)
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    total = serializers.IntegerField()
    percentage = serializers.FloatField()

class TeacherDashboardSerializer(serializers.Serializer):
    attendance_percentage = serializers.FloatField()
    class_count = serializers.IntegerField()
    lessons_count = serializers.IntegerField()
    task_count = serializers.IntegerField()
    task_completed = serializers.IntegerField()
    rank = serializers.IntegerField()

class TeacherLessonPlanGetSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    students = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = ("id", "group_name", "students")

    def get_students(self, obj):
        comments = LessonPlanStudents.objects.filter(
            lesson_plan=obj
        ).select_related("student", "student__user")

        comment_map = {
            c.student_id: c.comment
            for c in comments
        }

        students = obj.group.students.select_related("user").all()

        return [
            {
                "id": student.id,
                "name": student.user.name,
                "surname": student.user.surname,
                "comment": comment_map.get(student.id, "")
            }
            for student in students
        ]
