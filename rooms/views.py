from rest_framework import status
from .models import Room, RoomImages, RoomSubject
from .serializers import RoomSerializer, RoomImagesSerializer, RoomSubjectSerializer
from time_table.serializers import GroupTimeTable, GroupTimeTableSerializer
from rest_framework import generics
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['room', 'branch']
        permissions = check_user_permissions(user, table_names)

        queryset = Room.objects.all()
        serializer = RoomSerializer(queryset, many=True)
        return Response({'rooms': serializer.data, 'permissions': permissions})


class RoomRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        room.deleted = True
        room.save()
        return Response({"detail": "Room was deleted successfully"}, status=status.HTTP_200_OK)

    def get_group_time_tables(self, room_id):
        time_tables = GroupTimeTable.objects.filter(room_id=room_id)
        serializer = GroupTimeTableSerializer(time_tables, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['room', 'branch']
        permissions = check_user_permissions(user, table_names)
        room = self.get_object()
        time_tables_response = self.get_group_time_tables(room.id)
        room_data = self.get_serializer(room).data

        return Response({
            "room": room_data,
            "group_time_tables": time_tables_response.data,
            'permissions': permissions
        })


class RoomImagesListCreateView(generics.ListCreateAPIView):
    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomimages', 'room']
        permissions = check_user_permissions(user, table_names)

        queryset = RoomImages.objects.all()
        serializer = RoomImagesSerializer(queryset, many=True)
        return Response({'roomimages': serializer.data, 'permissions': permissions})


class RoomImagesRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomimages', 'room']
        permissions = check_user_permissions(user, table_names)
        room_images = self.get_object()
        room_images_data = self.get_serializer(room_images).data
        return Response({'roomimages': room_images_data, 'permissions': permissions})


class RoomSubjectListCreateView(generics.ListCreateAPIView):
    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomsubject', 'room']
        permissions = check_user_permissions(user, table_names)

        queryset = RoomSubject.objects.all()
        serializer = RoomSubjectSerializer(queryset, many=True)
        return Response({'roomsubjects': serializer.data, 'permissions': permissions})


class RoomSubjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomsubject', 'room']
        permissions = check_user_permissions(user, table_names)
        room_subject = self.get_object()
        room_subject_data = self.get_serializer(room_subject).data
        return Response({'roomsubject': room_subject_data, 'permissions': permissions})
