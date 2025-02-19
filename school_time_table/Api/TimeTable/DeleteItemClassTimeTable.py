from rest_framework import generics
from rest_framework.response import Response
from ...models import ClassTimeTable

from ...serializers import ClassTimeTableCreateUpdateSerializers



class DeleteItemClassTimeTable(generics.RetrieveDestroyAPIView):
    queryset = ClassTimeTable.objects.all()
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"msg": "Dars muvvaffaqqiyatli o'chirildi"})
