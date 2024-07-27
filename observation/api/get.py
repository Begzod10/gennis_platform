from rest_framework import generics
from observation.serializers import (ObservationDayListSerializers, ObservationStatisticsListSerializers)
from observation.models import ObservationDay, ObservationStatistics
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class ObservationStatisticsRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationstatistics', 'observationday', 'observationinfo', 'observationoption']
        permissions = check_user_permissions(user, table_names)
        observation_statistics = self.get_object()
        observation_statistics_data = self.get_serializer(observation_statistics).data
        return Response({'observationstatistic': observation_statistics_data, 'permissions': permissions})


class ObservationStatisticsListView(generics.ListAPIView):
    queryset = ObservationStatistics.objects.all()
    serializer_class = ObservationStatisticsListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationstatistics', 'observationday', 'observationinfo', 'observationoption']
        permissions = check_user_permissions(user, table_names)

        queryset = ObservationStatistics.objects.all()
        serializer = ObservationStatisticsListSerializers(queryset, many=True)
        return Response({'observationstatistics': serializer.data, 'permissions': permissions})


class ObservationDayRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDayListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationday', 'customuser', 'group', 'teacher']
        permissions = check_user_permissions(user, table_names)
        observation_day = self.get_object()
        observation_day_data = self.get_serializer(observation_day).data
        return Response({'observationday': observation_day_data, 'permissions': permissions})


class ObservationDayListView(generics.ListAPIView):
    queryset = ObservationDay.objects.all()
    serializer_class = ObservationDayListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationday', 'customuser', 'group', 'teacher']
        permissions = check_user_permissions(user, table_names)

        queryset = ObservationDay.objects.all()
        serializer = ObservationDayListSerializers(queryset, many=True)
        return Response({'observationdays': serializer.data, 'permissions': permissions})
