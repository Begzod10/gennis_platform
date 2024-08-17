from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from system.models import System
from teachers.models import Teacher
from group.models import Group
from attendances.models import AttendancePerDay, AttendancePerMonth


class OldIdRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        # `slug_field` ni `old_id` ga sozlash
        kwargs['slug_field'] = 'old_id'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        # `old_id` orqali obyektni olish
        model = self.queryset.model
        try:
            return model.objects.get(old_id=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with old_id {data} does not exist.")


class TransferAttendancePerMonthSerializer(serializers.ModelSerializer):
    student = OldIdRelatedField(queryset=Student.objects.all())
    teacher = OldIdRelatedField(queryset=Teacher.objects.all(), required=False, allow_null=True)
    group = OldIdRelatedField(queryset=Group.objects.all(), required=False, allow_null=True)

    class Meta:
        model = AttendancePerMonth
        fields = '__all__'


class TransferAttendancePerDaySerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id')
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id')
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id')
    month_date = serializers.JSONField(required=False, default=None)

    class Meta:
        model = AttendancePerDay
        fields = ['id', 'status', 'debt_per_day', 'salary_per_day', 'charity_per_day', 'day',
                  'homework_ball', 'dictionary_ball', 'activeness_ball', 'average', 'teacher', 'student',
                  'status', 'group', 'month_date', 'old_id']

    def create(self, validated_data):
        month_date = validated_data.pop('month_date')
        attendance_per_month = AttendancePerMonth.objects.filter(month_date=month_date).first()
        if attendance_per_month:
            attendance_per_day = AttendancePerDay.objects.create(**validated_data,
                                                                 attendance_per_month=attendance_per_month)
            return attendance_per_day
        else:
            attendance_per_day = AttendancePerDay.objects.create(**validated_data)
            return attendance_per_day
