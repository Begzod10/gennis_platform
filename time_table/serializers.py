from rest_framework import serializers

import time

from branch.models import Branch
from rooms.models import Room
from .models import WeekDays, GroupTimeTable
from group.models import Group
from group.serializers import GroupSerializer
from rooms.serializers import RoomCreateSerializer
from branch.serializers import BranchSerializer
from .functions.checkTime import check_time


class WeekDaysSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = WeekDays
        fields = ['id', 'name']


class GroupTimeTableCreateUpdateSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    week = serializers.PrimaryKeyRelatedField(queryset=WeekDays.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = GroupTimeTable
        fields = ['id', 'group', 'week', 'room', 'start_time', 'end_time', 'branch']

    def create(self, validated_data):
        result = check_time(validated_data.get('group'), validated_data.get('week').id, validated_data.get('room'),
                            validated_data.get('start_time'),
                            validated_data.get('end_time'))
        if result == True:
            group_time_table = GroupTimeTable.objects.create(
                **validated_data
            )
            return group_time_table
        else:
            raise serializers.ValidationError({"detail": result})

    def update(self, instance, validated_data):
        result = check_time(validated_data.get('group'), validated_data.get('week').id, validated_data.get('room'),
                            validated_data.get('start_time'),
                            validated_data.get('end_time'))
        if result == True:
            instance.group = validated_data.get('group', instance.group)
            instance.week = validated_data.get('week', instance.week)
            instance.room = validated_data.get('room', instance.room)
            instance.start_time = validated_data.get('start_time', instance.start_time)
            instance.end_time = validated_data.get('end_time', instance.end_time)
            instance.branch = validated_data.get('branch', instance.branch)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"detail": result})


class GroupTimeTableReadSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    week = WeekDaysSerializer()
    room = RoomCreateSerializer()
    branch = BranchSerializer()

    class Meta:
        model = GroupTimeTable
        fields = ['id', 'group', 'week', 'room', 'start_time', 'end_time', 'branch']
