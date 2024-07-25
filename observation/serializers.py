from rest_framework import serializers

from group.models import Group
from group.serializers import GroupSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer
from user.models import CustomUser
from user.serializers import UserSerializer
from .models import ObservationStatistics, ObservationDay, ObservationOptions, ObservationInfo


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


class ObservationDayListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    day = serializers.CharField(required=False)
    comment = serializers.CharField(required=False)
    average = serializers.IntegerField(required=False)
    user = UserSerializer(required=False)
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
