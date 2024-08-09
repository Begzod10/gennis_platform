from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher
from group.models import Group
from attendances.models import AttendancePerDay, AttendancePerMonth


class TransferAttendancePerMonthSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id')
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id')
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id')

    class Meta:
        model = AttendancePerMonth
        fields = ['id', 'status', 'total_debt', 'total_salary', 'ball_percentage', 'month_date',
                  'total_charity', 'remaining_debt', 'payment', 'remaining_salary', 'teacher', 'student',
                  'taken_salary', 'group']


class TransferAttendancePerDaySerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id')
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id')
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id')
    month_date = serializers.JSONField(required=False, default=None)

    class Meta:
        model = AttendancePerDay
        fields = ['id', 'status', 'debt_per_day', 'salary_per_day', 'charity_per_day', 'day',
                  'homework_ball', 'dictionary_ball', 'activeness_ball', 'average', 'teacher', 'student',
                  'status', 'group', 'month_date']

    def create(self, validated_data):
        attendance_per_month = AttendancePerMonth.objects.get(month_date=validated_data['month_date'])
        attendance_per_day = AttendancePerDay.objects.create(**validated_data,
                                                             attendance_per_month=attendance_per_month)
        return attendance_per_day
