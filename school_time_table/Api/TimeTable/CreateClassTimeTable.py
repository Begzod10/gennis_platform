from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from ...models import ClassTimeTable
from ...serializers import ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers, \
    ClassTimeTableLessonsSerializer

from group.serializers import GroupSerializer



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


class Classes(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.filter(class_number__isnull=False)
    serializer_class = GroupSerializer


class ClassTimeTableLessonsView(APIView):
    def get(self, request, pk):
        group = Group.objects.get(id=pk)
        serializer = ClassTimeTableLessonsSerializer(context={'group': group})
        data = {
            'time_tables': serializer.get_time_tables(None),
            'hours_list': serializer.get_hours_list(None)
        }
        return Response(data)
