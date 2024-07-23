# serializers.py
from rest_framework import serializers

from branch.serializers import BranchSerializer
from .models import Task, Branch


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
