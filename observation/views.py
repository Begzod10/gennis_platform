from rest_framework import generics
from .serializers import (ObservationInfoSerializers, ObservationOptionsSerializers)
from .models import ObservationInfo, ObservationOptions
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions
from .functions.creat_observation import creat_observation_info, creat_observation_options


class ObservationOptionsList(generics.ListAPIView):
    queryset = ObservationOptions.objects.all()
    serializer_class = ObservationOptionsSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationoptions']
        permissions = check_user_permissions(user, table_names)

        queryset = ObservationOptions.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = ObservationOptionsSerializers(queryset, many=True)
        creat_observation_options()
        return Response({'observationoption': serializer.data, 'permissions': permissions})


class ObservationOptionsRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = ObservationOptions.objects.all()
    serializer_class = ObservationOptionsSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationoptions']
        permissions = check_user_permissions(user, table_names)
        observation_options = self.get_object()
        observation_options_data = self.get_serializer(observation_options).data
        return Response({'observationoptions': observation_options_data, 'permissions': permissions})


class ObservationInfoList(generics.ListAPIView):
    queryset = ObservationInfo.objects.all()
    serializer_class = ObservationInfoSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationinfo']
        permissions = check_user_permissions(user, table_names)

        queryset = ObservationInfo.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = ObservationInfoSerializers(queryset, many=True)
        creat_observation_info()
        return Response({'observationinfos': serializer.data, 'permissions': permissions})


class ObservationInfoRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = ObservationInfo.objects.all()
    serializer_class = ObservationInfoSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['observationinfo']
        permissions = check_user_permissions(user, table_names)
        observation_info = self.get_object()
        observation_info_data = self.get_serializer(observation_info).data
        return Response({'observationinfo': observation_info_data, 'permissions': permissions})
