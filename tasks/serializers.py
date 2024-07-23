# serializers.py
from rest_framework import serializers

from branch.serializers import BranchSerializer
from students.serializers import StudentSerializer
from .models import Task, Branch, StudentCallInfo


class TaskSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()

    class Meta:
        model = Task
        fields = ['id', 'name', 'auth_group', 'branch']

    def create(self, validated_data):
        branch_data = validated_data.pop('branch', None)
        branch = Branch.objects.get(name=branch_data['name']) if isinstance(branch_data, dict) else None
        task = Task.objects.create(
            **validated_data,
            branch=branch
        )
        return task


class StudentCallInfoSerializers(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = StudentCallInfo
        fields = '__all__'
