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
    group_name = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = (
            "id",
            "group_name",
            "date",
            "objective",
            "main_lesson",
            "homework",
            "assessment",
            "activities",
            "resources",
            "students",
        )

    def get_group_name(self, obj):
        if obj.group:
            return obj.group.name
        if obj.flow:
            return obj.flow.name
        return None

    def get_students(self, obj):
        comments = getattr(obj, "_comments_cache", [])

        comment_map = {
            c.student_id: c.comment
            for c in comments
        }

        students = self._get_students(obj)

        return [
            {
                "id": s.id,
                "name": s.user.name,
                "surname": s.user.surname,
                "comment": comment_map.get(s.id, "")
            }
            for s in students
        ]

    def _get_students(self, obj):
        if obj.group_id:
            return obj.group.students.all()

        if obj.flow_id:
            return obj.flow.student_set.all()

        return []