from rest_framework import generics, status
from rest_framework.response import Response

from .models import Room, RoomImages, RoomSubject
from .serializers import RoomSerializer, RoomImagesSerializer, RoomSubjectSerializer
from time_table.serializers import GroupTimeTable, GroupTimeTableSerializer


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        room.deleted = True
        room.save()
        return Response({"detail": "Room was deleted successfully"}, status=status.HTTP_200_OK)

    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi
    def get_group_time_tables(self, room_id):
        time_tables = GroupTimeTable.objects.filter(room_id=room_id)
        serializer = GroupTimeTableSerializer(time_tables, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        room = self.get_object()
        time_tables_response = self.get_group_time_tables(room.id)
        room_data = self.get_serializer(room).data
        return Response({
            "room": room_data,
            "group_time_tables": time_tables_response.data
        })


class RoomImagesListCreateView(generics.ListCreateAPIView):
    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class RoomImagesRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class RoomSubjectListCreateView(generics.ListCreateAPIView):
    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class RoomSubjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi
