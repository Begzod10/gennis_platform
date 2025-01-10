from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from .models import FrontedPageType, FrontedPage, FrontedPageImage
from .serializers import FrontedPageTypeSerializer, FrontedPageSerializer, FrontedPageImageSerializer


class FrontedPageTypeViewSet(viewsets.ModelViewSet):
    queryset = FrontedPageType.objects.all()
    serializer_class = FrontedPageTypeSerializer
    # permission_classes = (IsSmm,)


class FrontedPageViewSet(viewsets.ModelViewSet):
    queryset = FrontedPage.objects.all().order_by('id')
    serializer_class = FrontedPageSerializer

    # permission_classes = (IsSmm,)

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'] != "undefined":
            instance = FrontedPage.objects.filter(type_id=kwargs['pk']).all()
            serializer = self.get_serializer(instance, many=True)
            return Response(serializer.data)
        return Response({"msg": 'Fronteddan hatolik bo\'ldi id o\'rniga undefined keldi!!!'},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({'message': 'deleted'}, status=status.HTTP_200_OK)


class FrontedPageImageViewSet(viewsets.ModelViewSet):
    queryset = FrontedPageImage.objects.all()
    serializer_class = FrontedPageImageSerializer
    # permission_classes = (IsSmm,)
