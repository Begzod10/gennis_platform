from rest_framework import serializers

from .models import Room, RoomImages, RoomSubject


class RoomSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=False)
    branch_id = serializers.CharField(max_length=100, required=True)
    seats_number = serializers.CharField(max_length=100, required=False)
    electronic_board = serializers.BooleanField(required=False)
    deleted = serializers.BooleanField(required=False)

    class Meta:
        model = Room
        fields = '__all__'


class RoomImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImages
        fields = '__all__'


class RoomSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomSubject
        fields = '__all__'
