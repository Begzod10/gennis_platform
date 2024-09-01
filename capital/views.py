from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from .models import CapitalCategory
from .serializers import (CapitalCategorySerializers)


class CreateCapitalCategoryList( generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CapitalCategory.objects.all()
    serializer_class = CapitalCategorySerializers

    def get(self, request, *args, **kwargs):
        queryset = CapitalCategory.objects.all()
        serializer = CapitalCategorySerializers(queryset, many=True)
        return Response(serializer.data)


class CapitalCategoryRetrieveUpdateDestroyAPIView(CustomResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CapitalCategory.objects.all()
    serializer_class = CapitalCategorySerializers

    def retrieve(self, request, *args, **kwargs):
        capital_category = self.get_object()
        capital_category_data = self.get_serializer(capital_category).data
        return Response(capital_category_data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'message': 'Capital category deleted successfully'}, status=200)
