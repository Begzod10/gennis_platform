from rest_framework import generics
from location.serializers import LocationListSerializers
from location.models import Location
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class LocationListAPIView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['location', 'system']
        permissions = check_user_permissions(user, table_names)

        queryset = Location.objects.all()
        serializer = LocationListSerializers(queryset, many=True)
        return Response({'locations': serializer.data, 'permissions': permissions})


class LocationRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['location', 'system']
        permissions = check_user_permissions(user, table_names)
        locations = self.get_object()
        location_data = self.get_serializer(locations).data
        return Response({'locations': location_data, 'permissions': permissions})
