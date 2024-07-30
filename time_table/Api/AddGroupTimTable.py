from rest_framework import generics
from rest_framework.views import APIView
import json
from rest_framework.response import Response

from group.models import Group
from rooms.models import Room
from time_table.models import GroupTimeTable

from time_table.serializers import GroupTimeTableSerializer
from time_table.functions.creatWeekDays import creat_week_days
from time_table.functions.checkTime import check_time
from time_table.functions.time_table_archive import creat_time_table_archive

class GroupTimeTableList(APIView):

    def post(self, request, group_id):
        creat_week_days()
        data = json.loads(request.body)
        result = check_time(group_id, data['week']['id'], data['room']['id'], data['branch']['id'],
                            data['start_time'], data['end_time'])
        creat_time_table_archive(group_id, data['week']['id'], data['room']['id'],
                   data['start_time'], data['end_time'])
        if result == True:
            serializer = GroupTimeTableSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"data": serializer.data})
        else:
            return Response(result)

    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        time_table = group.grouptimetable_set.all()
        serializers = GroupTimeTableSerializer(data=time_table, many=True)
        serializers.is_valid()
        return Response({"data": serializers.data})


