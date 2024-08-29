from rest_framework import generics
from rest_framework.response import Response

from permissions.functions.CheckUserPermissions import check_user_permissions
from permissions.response import CustomResponseMixin, QueryParamFilterMixin
from rooms.models import Room, RoomImages, RoomSubject
from rooms.serializers import RoomGetSerializer, RoomImagesGetSerializer, RoomSubjectGetSerializer
from time_table.serializers import GroupTimeTable, GroupTimeTableReadSerializer
from user.functions.functions import check_auth


class RoomListView(QueryParamFilterMixin, CustomResponseMixin, generics.ListAPIView):
    filter_mappings = {
        'teacher': 'group__teacher',
        'seats_number': 'seats_number',
        'electronic_board': 'electronic_board',
        'branch': 'branch',
        'deleted': 'deleted'

    }
    queryset = Room.objects.all()
    serializer_class = RoomGetSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['room', 'branch']
        permissions = check_user_permissions(user, table_names)

        queryset = Room.objects.all()

        queryset = self.filter_queryset(queryset)
        serializer = RoomGetSerializer(queryset, many=True)
        return Response({'rooms': serializer.data, 'permissions': permissions})


class RoomRetrieveView(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomGetSerializer

    def get_group_time_tables(self, room_id):
        time_tables = GroupTimeTable.objects.filter(room_id=room_id)
        serializer = GroupTimeTableReadSerializer(time_tables, many=True)
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


class RoomImagesListView(generics.ListAPIView):
    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesGetSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomimages', 'room']
        permissions = check_user_permissions(user, table_names)

        queryset = RoomImages.objects.all()
        serializer = RoomImagesGetSerializer(queryset, many=True)
        return Response({'roomimages': serializer.data, 'permissions': permissions})


class RoomImagesRetrieveView(generics.RetrieveAPIView):
    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesGetSerializer

    def retrieve(self, request, pk, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomimages', 'room']
        permissions = check_user_permissions(user, table_names)

        room_images = RoomImages.objects.filter(room_id=pk)

        room_images_data = self.get_serializer(room_images, many=True).data

        return Response({'roomimages': room_images_data, 'permissions': permissions})


class RoomSubjectListView(generics.ListAPIView):
    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectGetSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomsubject', 'room']
        permissions = check_user_permissions(user, table_names)

        queryset = RoomSubject.objects.all()
        serializer = RoomSubjectGetSerializer(queryset, many=True)
        return Response({'roomsubjects': serializer.data, 'permissions': permissions})


class RoomSubjectRetrieveView(generics.RetrieveAPIView):
    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectGetSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['roomsubject', 'room']
        permissions = check_user_permissions(user, table_names)
        room_subject = self.get_object()
        room_subject_data = self.get_serializer(room_subject).data
        return Response({'roomsubject': room_subject_data, 'permissions': permissions})
