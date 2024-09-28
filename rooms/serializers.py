from rest_framework import serializers

from branch.serializers import BranchSerializer, Branch
from subjects.serializers import Subject, SubjectSerializer
from .models import Room, RoomImages, RoomSubject


class RoomCreateSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Room
        fields = ['id', 'name', 'seats_number', 'electronic_board', 'deleted', 'branch']


class RoomGetSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(required=False)
    can_delete = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Room
        fields = ['id', 'name', 'seats_number', 'electronic_board', 'deleted', 'branch','can_delete']

    def get_can_delete(self, obj):
        status = None
        if obj.classtimetable_set.exists():
            status = True
        else:
            status = False

        return status


class RoomImagesGetSerializer(serializers.ModelSerializer):
    image = serializers.CharField()
    room = RoomGetSerializer(read_only=True)

    class Meta:
        model = RoomImages
        fields = ['id', 'image', 'room']


class RoomImagesCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())

    class Meta:
        model = RoomImages
        fields = ['id', 'image', 'room']


class RoomSubjectGetSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(required=False)
    room = RoomCreateSerializer(required=False)

    class Meta:
        model = RoomSubject
        fields = ['subject', 'room']


class RoomSubjectCreateSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())

    class Meta:
        model = RoomSubject
        fields = ['subject', 'room']
