from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from time_table.functions.creatWeekDays import creat_week_days
from time_table.models import GroupTimeTable
from time_table.serializers import GroupTimeTableReadSerializer, GroupTimeTableCreateUpdateSerializer


class CreateGroupTimeTable(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = GroupTimeTable.objects.all()
    serializer_class = GroupTimeTableCreateUpdateSerializer

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        creat_week_days()
        return GroupTimeTable.objects.filter(group_id=group_id)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GroupTimeTableReadSerializer
        return GroupTimeTableCreateUpdateSerializer

# class GroupTimeTableList(generics.ListCreateAPIView):
#     serializer_class = GroupTimeTableCreateUpdateSerializer
#
#     def get_queryset(self):
#         group_id = self.kwargs['group_id']
#         print(group_id)
#         creat_week_days()
#         return GroupTimeTable.objects.filter(group_id=group_id)
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return GroupTimeTableReadSerializer
#         return GroupTimeTableCreateUpdateSerializer
#
#     def create(self, request, *args, **kwargs):
#         creat_week_days()
#         data = json.loads(request.body)
#
#         result = check_time(data['group']['id'], data['week']['id'], data['room']['id'],
#                             data['branch']['id'],
#                             data['start_time'], data['end_time'])
#         creat_time_table_archive(data['group']['id'], data['week']['id'], data['room']['id'],
#                                  data['start_time'], data['end_time'])
#         if result == True:
#             serializer = GroupTimeTableReadSerializer(data=data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response({"data": serializer.data})
#         else:
#             return Response(result)
#
# def get(self, request, group_id):
#     creat_week_days()
#     group = Group.objects.get(pk=group_id)
#     time_table = group.grouptimetable_set.all()
#     serializers = GroupTimeTableReadSerializer(data=time_table, many=True)
#     serializers.is_valid()
#     return Response({"data": serializers.data})
