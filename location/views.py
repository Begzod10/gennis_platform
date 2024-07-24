from .serializers import (LocationSerializers)
from rest_framework import generics
from .models import Location
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class CreateLocationList(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['location', 'system']
        permissions = check_user_permissions(user, table_names)

        queryset = Location.objects.all()
        serializer = LocationSerializers(queryset, many=True)
        return Response({'locations': serializer.data, 'permissions': permissions})


class LocationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['location', 'system']
        permissions = check_user_permissions(user, table_names)
        locations = self.get_object()
        location_data = self.get_serializer(locations).data
        return Response({'locations': location_data, 'permissions': permissions})
