# serializers_list.py

# serializer.py

from datetime import datetime
from django.utils import timezone

from rest_framework import serializers

from branch.serializers import BranchSerializer
from students.serializers import StudentSerializer, Student
from user.models import CustomUser
from .models import Task, Branch, StudentCallInfo, Group, TaskStudent, TaskStatistics, TaskDailyStatistics, Mission


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
    student_tasks = serializers.PrimaryKeyRelatedField(queryset=TaskStudent.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = StudentCallInfo
        fields = ['id', 'student_tasks', 'student', 'task', 'delay_date', 'comment', 'user']

    def save(self, **kwargs):
        student_tasks = self.validated_data.get('student_tasks')
        student = student_tasks
        student.status = True
        student.save()

        student_call_info = super().save(**kwargs)

        # Updating TaskStatistics
        task_statistics = TaskStatistics.objects.get(task=student_call_info.task, day=datetime.now())
        task_statistics.progress_num -= 1
        task_statistics.completed_num += 1
        total_students = task_statistics.completed_num + task_statistics.progress_num
        task_statistics.percentage = (
                (task_statistics.completed_num / total_students) * 100) if total_students > 0 else 0

        task_statistics.save()

        # Updating TaskDailyStatistics
        daily_statistics = TaskStatistics.objects.filter(day=task_statistics.day, user=student_call_info.user).all()
        i = 0
        percentage = 0
        completed = 0
        for daily_statistic in daily_statistics:
            i += 1
            percentage += daily_statistic.percentage
            if daily_statistic.percentage == 100:
                completed += 1

        daily_statisticss = TaskDailyStatistics.objects.get(day=task_statistics.day, user=student_call_info.user)
        daily_statisticss.progress_num = i - completed
        daily_statisticss.completed_num = completed
        daily_statisticss.percentage = percentage / i if i > 0 else 0
        daily_statisticss.save()

        return student_call_info


class StudentCallInfoGetSerializers(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = StudentCallInfo
        fields = '__all__'


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.name} {obj.surname}"


class MissionCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = [
            "id", "title", "description",
            "executor", "reviewer",
            "deadline", "status", 'branch', 'creator',
            'comment'
        ]

    def create(self, validated_data):
        return Mission.objects.create(**validated_data)

    def update(self, instance, validated_data):
        status = validated_data.get('status', instance.status)
        if status == 'completed' and instance.finish_time is None:
            instance.finish_time = timezone.now().date()
            instance.delay_days = (instance.finish_time - instance.deadline).days
        return super().update(instance, validated_data)


class MissionDetailSerializer(serializers.ModelSerializer):
    creator = UserShortSerializer()
    executor = UserShortSerializer()
    reviewer = UserShortSerializer()
    delay_info = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = [
            "id",
            "title",
            "description",
            "creator",
            "executor",
            "reviewer",
            "start_time",
            "deadline",
            "finish_time",
            "status",
            "delay_info",
            "created_at",
            'branch',
            'comment'
        ]

    def get_delay_info(self, obj):
        if not obj.finish_time or not obj.deadline:
            return None

        diff_days = (obj.finish_time - obj.deadline).days
        if diff_days < 0:
            return f"{abs(diff_days)} kun erta tugatildi"
        elif diff_days > 0:
            return f"{diff_days} kun kech tugatildi"
        else:
            return "o‘z vaqtida tugatildi"
