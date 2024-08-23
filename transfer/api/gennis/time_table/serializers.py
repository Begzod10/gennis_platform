from time_table.models import WeekDays, GroupTimeTable
from rooms.models import Room
from rest_framework import serializers
from branch.models import Branch
from group.models import Group


class OldIdRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['slug_field'] = 'old_id'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        model = self.queryset.model
        try:
            return model.objects.get(old_id=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with old_id {data} does not exist.")


class WeekDaysSerializerTransfer(serializers.ModelSerializer):
    class Meta:
        model = WeekDays
        fields = ['id', 'name_en', 'name_uz', 'order']


class GroupTimeTableSerializerTransfer(serializers.ModelSerializer):
    group = OldIdRelatedField(queryset=Group.objects.all(), required=False, allow_null=True)
    room = OldIdRelatedField(queryset=Room.objects.all(), required=False, allow_null=True)
    branch = OldIdRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)
    week = serializers.SlugRelatedField(queryset=WeekDays.objects.all(), slug_field='name_en')

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
