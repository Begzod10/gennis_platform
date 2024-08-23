from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from ...models import ClassTimeTable
from ...serializers import ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers, \
    ClassTimeTableLessonsSerializer, ClassTimeTableLessonsTestSerializer

from group.serializers import GroupSerializer
from time_table.functions.creatWeekDays import creat_week_days
from time_table.models import WeekDays


class CreateClassTimeTable(generics.ListCreateAPIView):
    queryset = ClassTimeTable
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = ClassTimeTable.objects.get(pk=write_serializer.data['id'])
        read_serializer = ClassTimeTableReadSerializers(instance)

        return Response(read_serializer.data)



class Classes(generics.ListAPIView):
    queryset = Group.objects.filter(class_number__isnull=False)
    serializer_class = GroupSerializer
    def get_queryset(self):
        queryset = Group.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)

        return queryset


class ClassTimeTableLessonsView(APIView):
    def get(self, request, pk):
        creat_week_days()
        week = WeekDays.objects.get(id=pk)
        serializer = ClassTimeTableLessonsTestSerializer(context={'week': week})
        data = {
            'time_tables': serializer.get_time_tables(None),
            'hours_list': serializer.get_hours_list(None)
        }
        return Response(data)
    # def get(self, request, pk):
    #     creat_week_days()
    #     group = Group.objects.get(id=pk)
    #     serializer = ClassTimeTableLessonsSerializer(context={'group': group})
    #     data = {
    #         'time_tables': serializer.get_time_tables(None),
    #         'hours_list': serializer.get_hours_list(None)
    #     }
    #     return Response(data)
