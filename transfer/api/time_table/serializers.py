from django.db import transaction
from rest_framework import serializers
from group.models import Group
from time_table.models import WeekDays, GroupTimeTable
from rooms.models import Room
from branch.models import Branch


class WeekDaysSerializerTransfer(serializers.ModelSerializer):
    class Meta:
        model = WeekDays
        fields = ['id', 'name_en', 'name_uz', 'order']


class GroupTimeTableSerializerTransfer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id')
    week = serializers.SlugRelatedField(queryset=WeekDays.objects.all(), slug_field='name_en')
    room = serializers.SlugRelatedField(queryset=Room.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')

    class Meta:
        model = GroupTimeTable
        fields = ['id', 'group', 'week', 'room', 'start_time', 'end_time', 'branch', 'old_id']

    def create(self, validated_data):
        group = validated_data.get('group')
        group_time_table = GroupTimeTable.objects.create(**validated_data)
        for student in group.students.all():
            student.group_time_table.add(group_time_table)
        for teacher in group.teacher.all():
            teacher.group_time_table.add(group_time_table)
        return group_time_table
