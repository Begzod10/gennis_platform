from rest_framework import serializers
from teachers.models import Teacher
from subjects.models import Subject
from flows.models import Flow
from group.models import Group


class ActiveSubjectSerializerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name')


class ActiveListTeacherSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(required=False)
    surname = serializers.SerializerMethodField(required=False)
    age = serializers.SerializerMethodField(required=False)
    phone = serializers.SerializerMethodField(required=False)
    username = serializers.SerializerMethodField(required=False)
    subject = ActiveSubjectSerializerSerializer(many=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ('id', 'name', 'surname', 'username', 'age', 'phone', 'subject', 'status')

    def get_name(self, obj):
        return obj.user.name

    def get_username(self, obj):
        return obj.user.username

    def get_phone(self, obj):
        return obj.user.phone

    def get_age(self, obj):
        return obj.user.calculate_age()

    def get_surname(self, obj):
        return obj.user.surname

    def get_status(self, obj):
        flows = Flow.objects.filter(teacher=obj).exists()
        group = Group.objects.filter(teacher=obj).exists()
        if flows or group:
            return False
        else:
            return True


class ActiveListTeacherSerializerTime(serializers.ModelSerializer):
    name = serializers.CharField(required=False, source='user.name')
    surname = serializers.CharField(required=False, source='user.surname')
    username = serializers.CharField(required=False, source='user.username')

    class Meta:
        model = Teacher
        fields = ('id', 'name', 'surname', 'username','color')
