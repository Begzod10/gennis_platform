from rest_framework import viewsets

from .models import FrontedPageType, FrontedPage, FrontedPageImage
from .serializers import FrontedPageTypeSerializer, FrontedPageSerializer, FrontedPageImageSerializer


class FrontedPageTypeViewSet(viewsets.ModelViewSet):
    queryset = FrontedPageType.objects.all()
    serializer_class = FrontedPageTypeSerializer


class FrontedPageViewSet(viewsets.ModelViewSet):
    queryset = FrontedPage.objects.all()
    serializer_class = FrontedPageSerializer


class FrontedPageImageViewSet(viewsets.ModelViewSet):
    queryset = FrontedPageImage.objects.all()
    serializer_class = FrontedPageImageSerializer
