from rest_framework import serializers

from group.models import Group
from group.serializers import GroupSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from user.models import CustomUser
from user.serializers import UserSerializerRead
from .models import ObservationStatistics, ObservationDay, ObservationOptions, ObservationInfo, \
    TeacherObservationSchedule, TeacherObservationCycle
from observation.uitils import get_week_date_range
from django.db import models


class ObservationInfoSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = ObservationInfo
        fields = ['id', 'title']


class ObservationOptionsSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    value = serializers.IntegerField(required=False)

    class Meta:
        model = ObservationOptions
        fields = ['id', 'name', 'value']


class ObservationDaySerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    day = serializers.CharField(required=False)
    comment = serializers.CharField(required=False)
    average = serializers.IntegerField(required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())

    class Meta:
        model = ObservationDay
        fields = ['id', 'day', 'comment', 'average', 'user', 'group', 'teacher']

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance


class ObservationDayListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    day = serializers.CharField(required=False)
    comment = serializers.CharField(required=False)
    average = serializers.IntegerField(required=False)
    user = UserSerializerRead(required=False)
    group = GroupSerializer(required=False)
    teacher = TeacherSerializer(required=False)

    class Meta:
        model = ObservationDay
        fields = ['id', 'day', 'comment', 'average', 'user', 'group', 'teacher']


class ObservationStatisticsSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    comment = serializers.CharField(required=False)
    observation_day = serializers.PrimaryKeyRelatedField(queryset=ObservationDay.objects.all())
    observation_info = serializers.PrimaryKeyRelatedField(queryset=ObservationInfo.objects.all())
    observation_option = serializers.PrimaryKeyRelatedField(queryset=ObservationOptions.objects.all())

    class Meta:
        model = ObservationStatistics
        fields = ['id', 'comment', 'observation_day', 'observation_info', 'observation_option']


class ObservationStatisticsListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    comment = serializers.CharField(required=False)
    observation_day = ObservationDaySerializers(required=False)
    observation_info = ObservationInfoSerializers(required=False)
    observation_option = ObservationOptionsSerializers(required=False)

    class Meta:
        model = ObservationStatistics
        fields = ['id', 'comment', 'observation_day', 'observation_info', 'observation_option']


class ObserverScheduleSerializer(serializers.ModelSerializer):
    observer_id = serializers.IntegerField(source='observer.id')
    observer_name = serializers.SerializerMethodField()
    is_completed = serializers.BooleanField()
    observation_avg = serializers.SerializerMethodField()

    class Meta:
        model = TeacherObservationSchedule
        fields = ['observer_id', 'observer_name', 'is_completed', 'observation_avg']

    def get_observer_name(self, obj):
        user = obj.observer.user
        return f"{user.name or ''} {user.surname or ''}".strip()

    def get_observation_avg(self, obj):
        if obj.observation_day:
            return obj.observation_day.average
        return None


class TeacherWeeklyObservationSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    teacher_name = serializers.CharField()
    total_observers_required = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    weekly_avg_score = serializers.FloatField(allow_null=True)
    observers = ObserverScheduleSerializer(many=True)
