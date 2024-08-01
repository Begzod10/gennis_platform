from rest_framework import serializers

from students.models import Student
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from .models import Group

from students.serializers import StudentSerializer
from group.serializers import GroupSerializer
from .models import AttendancePerDay, AttendancePerMonth


class AttendancePerMonthSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    teacher = TeacherSerializer()
    group = GroupSerializer()

    class Meta:
        model = AttendancePerMonth
        fields = ['id', 'status', 'total_debt', 'total_salary', 'ball_percentage', 'month_date',
                  'total_charity', 'remaining_debt', 'payment', 'remaining_salary', 'teacher', 'student',
                  'taken_salary', 'group']


class AttendancePerDaySerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    teacher = TeacherSerializer()
    group = GroupSerializer()
    attendance_per_month = AttendancePerMonthSerializer()

    class Meta:
        model = AttendancePerDay
        fields = ['id', 'status', 'debt_per_day', 'salary_per_day', 'charity_per_day', 'day',
                  'homework_ball', 'dictionary_ball', 'activeness_ball', 'average', 'teacher', 'student',
                  'status', 'group', 'attendance_per_month']


class AttendancePerDayCreateUpdateSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    teachers = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    attendance_per_month = serializers.PrimaryKeyRelatedField(queryset=AttendancePerMonth.objects.all())

    class Meta:
        model = AttendancePerDay
        fields = ['id', 'status', 'debt_per_day', 'salary_per_day', 'charity_per_day', 'day',
                  'homework_ball', 'dictionary_ball', 'activeness_ball', 'average', 'teacher', 'student',
                  'status', 'group', 'attendance_per_month']


