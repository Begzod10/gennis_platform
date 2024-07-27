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

    class Meta:
        model = Room
        fields = ['id', 'name', 'seats_number', 'electronic_board', 'deleted', 'branch']


class RoomImagesGetSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    room = RoomGetSerializer(required=False)

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
