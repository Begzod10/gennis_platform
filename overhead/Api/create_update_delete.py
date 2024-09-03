from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from overhead.models import Overhead
from overhead.serializers import OverheadSerializerCreate
from permissions.response import CustomResponseMixin


class OverheadCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate


class OverheadUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate


class OverheadDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()

        return Response({"msg": "muvaffaqiyatlik o'chirildi"}, status=status.HTTP_200_OK)
