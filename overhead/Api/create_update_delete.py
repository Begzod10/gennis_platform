from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from overhead.models import Overhead
from overhead.serializers import OverheadSerializerCreate
from permissions.response import CustomResponseMixin
from overhead.serializer.lists import ActiveListTeacherSerializer

class OverheadCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        instance = serializer.instance

        return Response(
            ActiveListTeacherSerializer(instance).data,
            status=status.HTTP_200_OK,
            headers=headers
        )


class OverheadUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        updated_instance = serializer.instance

        return Response(
            ActiveListTeacherSerializer(updated_instance).data,
            status=status.HTTP_200_OK
        )

class OverheadDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerCreate

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()

        return Response({"msg": "muvaffaqiyatlik o'chirildi"}, status=status.HTTP_200_OK)
