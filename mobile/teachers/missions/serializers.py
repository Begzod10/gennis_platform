from rest_framework import serializers
from tasks.models import Mission, MissionComment
from tasks.serializers import UserShortSerializer, MissionCommentDetailSerializer, MissionProofSerializer, \
    MissionAttachmentSerializer, MissionSubtaskSerializer
from django.utils import timezone


class MobileMissionSerializer(serializers.ModelSerializer):
    deadline = serializers.DateField(format="%Y-%m-%d")
    creator = UserShortSerializer()
    executor = UserShortSerializer()
    deadline_color = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = [
            "id",
            "title",
            "status",
            "deadline",
            "deadline_color",
            "creator",
            "executor",
            "is_redirected",
        ]

    def get_deadline_color(self, obj):
        if not obj.deadline:
            return "grey"

        today = timezone.now().date()
        diff = (obj.deadline - today).days

        if diff <= 1:
            return "red"
        elif diff <= 4:
            return "yellow"
        return "green"


class MobileMissionDetailSerializer(serializers.ModelSerializer):
    creator = UserShortSerializer()
    executor = UserShortSerializer()
    reviewer = UserShortSerializer()
    comments = MissionCommentDetailSerializer(many=True)
    attachments = MissionAttachmentSerializer(many=True)
    proofs = MissionProofSerializer(many=True)
    subtasks = MissionSubtaskSerializer(many=True)

    class Meta:
        model = Mission
        fields = "__all__"


class MobileMissionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ["status"]


class MobileMissionCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionComment
        fields = ["text"]


class MobileMissionCommentSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = MissionComment
        fields = ["id", "user", "text", "created_at"]
