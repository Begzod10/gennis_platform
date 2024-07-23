# serializers.py
from rest_framework import serializers

from branch.serializers import BranchSerializer
from students.serializers import Student, StudentSerializer
from user.models import CustomUser
from .models import Task, Branch, StudentCallInfo, Group


class TaskSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    auth_group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Task
        fields = ['id', 'name', 'auth_group', 'branch']


class TaskGetSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'auth_group', 'branch']


class StudentCallInfoCreateUpdateDeleteSerializers(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = StudentCallInfo
        fields = ['id', 'student', 'task', 'delay_date', 'comment', 'user']


class StudentCallInfoGetSerializers(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = StudentCallInfo
        fields = '__all__'
