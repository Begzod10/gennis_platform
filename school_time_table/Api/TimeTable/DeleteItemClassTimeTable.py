from rest_framework import generics

from ...models import ClassTimeTable

from ...serializers import DeleteItemTimeTableSerializers


class DeleteItemClassTimeTable(generics.RetrieveUpdateAPIView):
    queryset = ClassTimeTable
    serializer_class = DeleteItemTimeTableSerializers
