from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .functions.creat_observation import creat_observation_info, creat_observation_options
from .models import ObservationInfo, ObservationOptions
from .serializers import (ObservationInfoSerializers, ObservationOptionsSerializers)


class ObservationOptionsList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationOptions.objects.all()
    serializer_class = ObservationOptionsSerializers

    def get(self, request, *args, **kwargs):

        queryset = ObservationOptions.objects.all()
        serializer = ObservationOptionsSerializers(queryset, many=True)
        creat_observation_options()
        return Response(serializer.data)


class ObservationOptionsRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationOptions.objects.all()
    serializer_class = ObservationOptionsSerializers

    def retrieve(self, request, *args, **kwargs):
        observation_options = self.get_object()
        observation_options_data = self.get_serializer(observation_options).data
        return Response(observation_options_data)


class ObservationInfoList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationInfo.objects.all()
    serializer_class = ObservationInfoSerializers

    def get(self, request, *args, **kwargs):

        queryset = ObservationInfo.objects.all()
        serializer = ObservationInfoSerializers(queryset, many=True)
        creat_observation_info()
        return Response(serializer.data)


class ObservationInfoRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ObservationInfo.objects.all()
    serializer_class = ObservationInfoSerializers

    def retrieve(self, request, *args, **kwargs):
        observation_info = self.get_object()
        observation_info_data = self.get_serializer(observation_info).data
        return Response(observation_info_data)
