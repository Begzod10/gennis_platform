# serializers_list.py

# serializer.py
from datetime import datetime, date
from django.utils import timezone

from rest_framework import serializers

from branch.serializers import BranchSerializer
from students.serializers import StudentSerializer, Student
from user.models import CustomUser
from .models import Task, Branch, StudentCallInfo, Group, TaskStudent, TaskStatistics, TaskDailyStatistics, Mission, \
    MissionSubtask, MissionAttachment, MissionComment, MissionProof, Tag, Notification


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class MissionCrudSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    executor_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=CustomUser.objects.all()
        ),
        write_only=True
    )
    reviewer = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True, required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), allow_null=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)

    class Meta:
        model = Mission
        fields = [
            "id", "title", "description", 'creator',
            "category", "tags",
            "executor_ids", "redirected_by_id", "reviewer", "branch",
            "deadline", "status", "is_redirected",
            "kpi_weight", "penalty_per_day",
            "is_recurring", "recurring_type", 'final_sc'
        ]

    def create(self, validated_data):
        executor_ids = validated_data.pop("executor_ids")
        tags = validated_data.pop("tags", [])

        missions = []

        for executor in executor_ids:
            mission = Mission.objects.create(
                executor=executor,
                **validated_data
            )
            if tags:
                mission.tags.set(tags)

            missions.append(mission)

        return missions  # 👈 LIST qaytaramiz

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)

        executor_ids = validated_data.pop("executor_ids", None)

        if executor_ids:
            new_executor = executor_ids[0]
            instance.is_redirected = True
            instance.redirected_by_id = new_executor.id
            instance.redirected_at = timezone.now()
        else:
            instance.is_redirected = False
            instance.redirected_by = None
            instance.redirected_at = None

        status = validated_data.get("status", instance.status)

        if status == "completed" and not instance.finish_date:
            instance.finish_date = timezone.now().date()
            instance.calculate_delay_days()
            instance.final_sc = instance.final_score()

        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.set(tags)

        return instance


class MissionSubtaskSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=Mission.objects.all())

    class Meta:
        model = MissionSubtask
        fields = ["id", "mission", "title", "is_done", "order"]


class MissionAttachmentSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=Mission.objects.all())
    file = serializers.FileField(required=False, allow_null=True)
    uploaded_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = MissionAttachment
        fields = ["id", "mission", "file", "note", "uploaded_at"]
        read_only_fields = ["uploaded_at"]


class MissionCommentSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=Mission.objects.all())
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = MissionComment
        fields = ["id", "mission", "text", "attachment", "created_at", "user"]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        return super().create(validated_data)


class MissionCommentDetailSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=Mission.objects.all())
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    user = UserShortSerializer()

    class Meta:
        model = MissionComment
        fields = ["id", "mission", "text", "attachment", "created_at", "user"]
        read_only_fields = ["created_at"]


class MissionProofSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=Mission.objects.all())
    file = serializers.FileField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = MissionProof
        fields = ["id", "mission", "file", "comment", "created_at"]
        read_only_fields = ["created_at"]


class MissionDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    start_date = serializers.DateField(format="%Y-%m-%d", read_only=True)
    deadline = serializers.DateField(format="%Y-%m-%d", read_only=True)
    finish_date = serializers.DateField(format="%Y-%m-%d", read_only=True)
    redirected_at = serializers.DateTimeField(format="%Y-%m-%d", allow_null=True)
    creator = UserShortSerializer()
    executor = UserShortSerializer()
    reviewer = UserShortSerializer()
    redirected_by = UserShortSerializer()
    subtasks = MissionSubtaskSerializer(many=True, read_only=True)
    attachments = MissionAttachmentSerializer(many=True, read_only=True)
    comments = MissionCommentDetailSerializer(many=True, read_only=True)
    proofs = MissionProofSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    delay_info = serializers.SerializerMethodField()
    deadline_color = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = [
            "id", "title", "description", "category", "tags",
            "creator", "executor", "reviewer", "redirected_by", "branch",
            "start_date", "deadline", "finish_date", "is_redirected", "redirected_at",
            "status", "delay_days", "delay_info",
            "kpi_weight", "penalty_per_day", "is_recurring", "recurring_type",
            "subtasks", "attachments", "comments", "proofs", "created_at", 'final_sc', 'deadline_color'
        ]

    def get_delay_info(self, obj):
        if not obj.finish_date or not obj.deadline:
            return None
        diff_days = (obj.finish_date - obj.deadline).days
        if diff_days < 0:
            return f"{abs(diff_days)} kun erta tugatildi"
        elif diff_days > 0:
            return f"{diff_days} kun kech tugatildi"
        return "o‘z vaqtida tugatildi"

    def get_deadline_color(self, obj):
        if not obj.deadline:
            return "grey"

        today = date.today()
        remaining_days = (obj.deadline - today).days

        if remaining_days <= 1:
            return "red"
        elif 2 <= remaining_days <= 4:
            return "yellow"
        else:
            return "green"


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    deadline = serializers.DateField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "message",
            "role",
            "mission",
            "deadline",
            "is_read",
            "created_at",
        ]
