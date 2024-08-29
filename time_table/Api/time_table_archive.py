from rest_framework import generics
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions
from time_table.models import TimeTableArchive
from time_table.serializers import TimeTableArchiveListSerializer


class TimeTableArchiveRetrieveAPIView(generics.RetrieveAPIView):
    queryset = TimeTableArchive.objects.all()
    serializer_class = TimeTableArchiveListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['timetablearchive', 'group', 'week', 'room']
        permissions = check_user_permissions(user, table_names)
        time_table_archive = self.get_object()
        time_table_archive_data = self.get_serializer(time_table_archive).data
        return Response({'timetablearchive': time_table_archive_data, 'permissions': permissions})


class TimeTableArchiveListView(generics.ListAPIView):
    queryset = TimeTableArchive.objects.all()
    serializer_class = TimeTableArchiveListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['timetablearchive', 'group', 'week', 'room']
        permissions = check_user_permissions(user, table_names)

        queryset = TimeTableArchive.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = TimeTableArchiveListSerializer(queryset, many=True)
        return Response({'timetablearchives': serializer.data, 'permissions': permissions})
