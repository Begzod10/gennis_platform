from rest_framework import generics

from rest_framework.response import Response

from time_table.models import GroupTimeTable

from time_table.serializers import GroupTimeTableReadSerializer, GroupTimeTableCreateUpdateSerializer
from time_table.functions.creatWeekDays import creat_week_days


class GroupTimeTableList(generics.ListCreateAPIView):
    serializer_class = GroupTimeTableCreateUpdateSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id')
        return GroupTimeTable.objects.filter(group_id=id)

    def create(self, request, *args, **kwargs):
        creat_week_days()
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = GroupTimeTable.objects.get(pk=write_serializer.data['id'])
        read_serializer = GroupTimeTableReadSerializer(instance)

        return Response(read_serializer.data)
