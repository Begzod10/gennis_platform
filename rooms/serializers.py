from rest_framework import serializers

from .models import Room, RoomImages, RoomSubject


class RoomSerializer(serializers.ModelSerializer):
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
