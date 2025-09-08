from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import QueryParamFilterMixin
from rooms.models import Room, RoomImages, RoomSubject
from rooms.serializers import RoomGetSerializer, RoomImagesGetSerializer, RoomSubjectGetSerializer
from time_table.serializers import GroupTimeTable, GroupTimeTableReadSerializer


class RoomListView(QueryParamFilterMixin, generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    filter_mappings = {
        'teacher': 'group__teacher',
        'seats_number': 'seats_number',
        'electronic_board': 'electronic_board',
        'branch': 'branch_id',
        'deleted': 'deleted'

    }
    queryset = Room.objects.all().order_by('id')
    serializer_class = RoomGetSerializer


class RoomListViewClassroom(QueryParamFilterMixin, generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    queryset = Room.objects.all().order_by('id')
    serializer_class = RoomGetSerializer


class RoomRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Room.objects.all()
    serializer_class = RoomGetSerializer

    def get_group_time_tables(self, room_id):
        time_tables = GroupTimeTable.objects.filter(room_id=room_id)
        serializer = GroupTimeTableReadSerializer(time_tables, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        room = self.get_object()
        time_tables_response = self.get_group_time_tables(room.id)
        room_data = self.get_serializer(room).data

        return Response({
            "room": room_data,
            "group_time_tables": time_tables_response.data,
        })


class RoomImagesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesGetSerializer

    def get(self, request, *args, **kwargs):
        queryset = RoomImages.objects.all()
        serializer = RoomImagesGetSerializer(queryset, many=True)
        return Response(serializer.data)


class RoomImagesRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomImages.objects.all()
    serializer_class = RoomImagesGetSerializer

    def retrieve(self, request, pk, *args, **kwargs):
        room_images = RoomImages.objects.filter(room_id=pk)

        room_images_data = self.get_serializer(room_images, many=True).data

        return Response(room_images_data)


class RoomSubjectListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectGetSerializer

    def get(self, request, *args, **kwargs):
        queryset = RoomSubject.objects.all()
        serializer = RoomSubjectGetSerializer(queryset, many=True)
        return Response(serializer.data)


class RoomSubjectRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = RoomSubject.objects.all()
    serializer_class = RoomSubjectGetSerializer

    def retrieve(self, request, *args, **kwargs):
        room_subject = self.get_object()
        room_subject_data = self.get_serializer(room_subject).data
        return Response(room_subject_data)
