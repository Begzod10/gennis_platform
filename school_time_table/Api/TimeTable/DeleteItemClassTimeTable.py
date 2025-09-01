from rest_framework import generics
from rest_framework.response import Response
from ...models import ClassTimeTable

from ...serializers import ClassTimeTableCreateUpdateSerializers


class DeleteItemClassTimeTable(generics.RetrieveDestroyAPIView):
    queryset = ClassTimeTable.objects.all()
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        # Serializerga instance berish kerak
        serializer = self.get_serializer(instance)

        # Avval flask serverdan o‘chirib tashlaymiz
        # flask_response, status_code = serializer.delete_from_flask(instance)

        # Keyin Django bazadan o‘chirish
        self.perform_destroy(instance)

        return Response({
            "msg": "Dars muvvaffaqqiyatli o'chirildi",
            "flask_response": flask_response
        }, status=200)
