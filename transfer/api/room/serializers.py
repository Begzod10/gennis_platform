from rest_framework import serializers
from branch.models import Branch
from rooms.models import Room, RoomImages, RoomSubject
from subjects.models import Subject


class TransferRoomsCreateUpdateSerializer(serializers.ModelSerializer):
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')

    class Meta:
        model = Room
        fields = ['id', 'name', 'seats_number', 'electronic_board', 'deleted', 'branch', 'old_id']


class TransferRoomImagesCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    room = serializers.SlugRelatedField(queryset=Room.objects.all(), slug_field='old_id')

    class Meta:
        model = RoomImages
        fields = ['id', 'image', 'room', 'old_id']


class TransferRoomSubjectsCreateSerializer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(queryset=Subject.objects.all(), slug_field='old_id')
    room = serializers.SlugRelatedField(queryset=Room.objects.all(), slug_field='old_id')

    class Meta:
        model = RoomSubject
        fields = ['id', 'subject', 'room']
