from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils.timezone import localtime
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from attendances.models import AttendancePerDay
from group.serializers import GroupCreateUpdateSerializer
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