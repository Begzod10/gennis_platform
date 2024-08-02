from rest_framework import generics
from rest_framework.response import Response
from time_table.models import GroupTimeTable
from time_table.serializers import GroupTimeTableReadSerializer, GroupTimeTableCreateUpdateSerializer
from time_table.functions.creatWeekDays import creat_week_days
from time_table.functions.checkTime import check_time
from time_table.functions.time_table_archive import creat_time_table_archive


class GroupTimeTableList(generics.ListCreateAPIView):
    serializer_class = GroupTimeTableCreateUpdateSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id')
        return GroupTimeTable.objects.filter(group_id=id)

    def create(self, request, *args, **kwargs):
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
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        instance = GroupTimeTable.objects.get(pk=write_serializer.data['id'])
        read_serializer = GroupTimeTableReadSerializer(instance)
        return Response(read_serializer.data)
