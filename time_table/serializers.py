from rest_framework import serializers

import time

from branch.models import Branch
from rooms.models import Room
from .models import WeekDays, GroupTimeTable
from group.models import Group
from group.serializers import GroupSerializer
from rooms.serializers import RoomCreateSerializer
from branch.serializers import BranchSerializer


class WeekDaysSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = WeekDays
        fields = ['id', 'name']


class GroupTimeTableSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    week = WeekDaysSerializer()
    room = RoomCreateSerializer()
    branch = BranchSerializer()

    class Meta:
        model = GroupTimeTable
        fields = ['id', 'group', 'week', 'room', 'start_time', 'end_time', 'branch']

    def create(self, validated_data):
        group_data = validated_data.pop('group')
        week_data = validated_data.pop('week')
        room_data = validated_data.pop('room')
        branch_data = validated_data.pop('branch')
        group = Group.objects.get(id=group_data['id'])
        week = WeekDays.objects.get(id=week_data['id'])
        room = Room.objects.get(id=room_data['id'])
        branch = Branch.objects.get(id=branch_data['id'])
        group_time_table = GroupTimeTable.objects.create(
            group=group,
            week=week,
            room=room,
            branch=branch,
            **validated_data
        )
        return group_time_table

    def update(self, instance, validated_data):
        group = Group.objects.get(pk=validated_data.pop('group')['id'])
        week = WeekDays.objects.get(pk=validated_data.pop('week')['id'])
        room = Room.objects.get(pk=validated_data.pop('room')['id'])
        branch = Branch.objects.get(pk=validated_data.pop('branch')['id'])
        instance.group = group
        instance.week = week
        instance.room = room
        instance.branch = branch
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.save()
        return instance
