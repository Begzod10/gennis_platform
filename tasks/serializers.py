# serializers.py
from rest_framework import serializers

from branch.serializers import BranchSerializer
from students.serializers import Student
from .models import Task, Branch, StudentCallInfo, Group


class TaskSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), many=True)
    auth_group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'auth_group', 'branch']


class TaskGetSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'auth_group', 'branch']


class StudentCallInfoCreateUpdateDeleteSerializers(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), many=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True)

    class Meta:
        model = StudentCallInfo
        fields = '__all__'
