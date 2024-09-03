from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from rooms.models import Room, RoomImages, RoomSubject
from rooms.serializers import RoomCreateSerializer, RoomImagesCreateSerializer, RoomSubjectCreateSerializer


class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomCreateSerializer


class RoomDeleteView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Room.objects.all()
    serializer_class = RoomCreateSerializer

    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        room.deleted = True
        room.save()
        return Response({"detail": "Room was deleted successfully"}, status=status.HTTP_200_OK)


class RoomUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Room.objects.all()
    serializer_class = RoomCreateSerializer


class RoomImagesCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesCreateSerializer


class RoomImagesUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesCreateSerializer


class RoomImagesDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesCreateSerializer


class RoomSubjectCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectCreateSerializer


class RoomSubjectUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectCreateSerializer


class RoomSubjectDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectCreateSerializer
