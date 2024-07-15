from rest_framework import serializers

from .models import Room, RoomImages, RoomSubject


class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=100, required=False)
    # branch_id = serializers.CharField(max_length=100, required=False)
    branch = serializers.CharField(required=False)
    seats_number = serializers.CharField(max_length=100, required=False)
    electronic_board = serializers.CharField(max_length=100, required=False)
    deleted = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Room
        fields = ['id', 'name', 'seats_number', 'electronic_board', 'deleted', 'branch']


class RoomImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImages
        fields = '__all__'


class RoomSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomSubject
        fields = '__all__'
