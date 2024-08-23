from rest_framework import generics
from rest_framework.response import Response

from ...models import ClassTimeTable
from ...serializers import ClassTimeTableCreateUpdateSerializers, ClassTimeTableReadSerializers


class UpdateClassTimeTable(generics.UpdateAPIView):
    queryset = ClassTimeTable.objects.all()
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def update(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)

        instance = ClassTimeTable.objects.get(pk=write_serializer.data['id'])
        read_serializer = ClassTimeTableReadSerializers(instance)

        return Response(read_serializer.data)
