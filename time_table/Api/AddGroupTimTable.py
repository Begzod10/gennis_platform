import json
from rest_framework import generics
from rest_framework.response import Response
from time_table.models import GroupTimeTable
from time_table.serializers import GroupTimeTableReadSerializer, GroupTimeTableCreateUpdateSerializer
from time_table.functions.creatWeekDays import creat_week_days
from time_table.functions.checkTime import check_time
from time_table.functions.time_table_archive import creat_time_table_archive
from group.models import Group


class GroupTimeTableList(generics.ListCreateAPIView):
    serializer_class = GroupTimeTableCreateUpdateSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id')
        creat_week_days()
        return GroupTimeTable.objects.filter(group_id=id)

    def create(self, request, *args, **kwargs):
        creat_week_days()
        data = json.loads(request.body)
        result = check_time(data['group']['id'], data['week']['id'], data['room']['id'],
                            data['branch']['id'],
                            data['start_time'], data['end_time'])
        creat_time_table_archive(data['group']['id'], data['week']['id'], data['room']['id'],
                                 data['start_time'], data['end_time'])
        if result == True:
            serializer = GroupTimeTableReadSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"data": serializer.data})
        else:
            return Response(result)

    def get(self, request, group_id):
        creat_week_days()
        group = Group.objects.get(pk=group_id)
        time_table = group.grouptimetable_set.all()
        serializers = GroupTimeTableReadSerializer(data=time_table, many=True)
        serializers.is_valid()
        return Response({"data": serializers.data})
