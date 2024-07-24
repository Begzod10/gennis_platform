from rest_framework import generics
from rest_framework.response import Response

from ...models import ClassTimeTable
from ...serializers import ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers


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
