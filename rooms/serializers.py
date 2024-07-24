from rest_framework import serializers
from branch.serializers import BranchSerializer
from .models import Room, RoomImages, RoomSubject
from subjects.serializers import SubjectSerializer


class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=100, required=False)
    branch = BranchSerializer(required=False)
    seats_number = serializers.CharField(max_length=100, required=False)
    electronic_board = serializers.BooleanField(required=False)
    deleted = serializers.BooleanField(required=False)

    class Meta:
        model = Room
        fields = ['id', 'name', 'seats_number', 'electronic_board', 'deleted', 'branch']


class RoomImagesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    image = serializers.ImageField()
    room = RoomSerializer(required=False)

    class Meta:
        model = RoomImages
        fields = ['id', 'image', 'room']


class RoomSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(required=False)
    room = RoomSerializer(required=False)

    class Meta:
        model = RoomSubject
        fields = ['subject', 'room']
