from rest_framework import serializers
from .models import Report, AdminRequest, RequestComment


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"


class RequestCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = RequestComment
        fields = "__all__"


class AdminRequestSerializer(serializers.ModelSerializer):
    branch_name = serializers.ReadOnlyField(source='branch.name')
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    comments = RequestCommentSerializer(many=True, read_only=True)

    class Meta:
        model = AdminRequest
        fields = "__all__"


