from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from ...models import Hours
from ...serializers import HoursSerializers


class HourUpdateDeleteView(CustomResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Hours.objects.all()
    serializer_class = HoursSerializers

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Hours was deleted successfully"}, status=status.HTTP_200_OK)
