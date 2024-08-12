from rest_framework import generics
from rest_framework.response import Response

from .serializers import TransferRoomsCreateUpdateSerializer, TransferRoomImagesCreateSerializer, \
    TransferRoomSubjectsCreateSerializer
from rooms.serializers import RoomGetSerializer, RoomImagesGetSerializer, RoomSubjectGetSerializer
from rooms.models import Room, RoomImages, RoomSubject


class TransferCreatRooms(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = TransferRoomsCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = Room.objects.get(pk=write_serializer.data['id'])
        read_serializer = RoomGetSerializer(instance)
        return Response(read_serializer.data)


class TransferCreatRoomImages(generics.ListCreateAPIView):
    queryset = RoomImages.objects.all()
    serializer_class = TransferRoomImagesCreateSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        instance = RoomImages.objects.get(pk=write_serializer.data['id'])
        read_serializer = RoomImagesGetSerializer(instance)
        return Response(read_serializer.data)


class TransferCreatRoomSubjects(generics.ListCreateAPIView):
    queryset = RoomSubject.objects.all()
    serializer_class = TransferRoomSubjectsCreateSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        instance = RoomSubject.objects.get(pk=write_serializer.data['id'])
        read_serializer = RoomSubjectGetSerializer(instance)
        return Response(read_serializer.data)
