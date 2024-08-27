from rest_framework import generics
from rest_framework.response import Response

from location.models import Location
from location.serializers import LocationListSerializers, LocationListSerializersWithBranch
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth


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


class LocationsForSystem(generics.ListAPIView):
    serializer_class = LocationListSerializers
    queryset = Location.objects.all()

    def post(self, request, *args, **kwargs):
        systems = request.data.get('systems', [])
        locations = Location.objects.filter(system__in=systems)

        if locations.count() == 1:
            serializer = LocationListSerializers(locations.first())
        else:
            serializer = LocationListSerializers(locations, many=True)

        return Response(serializer.data)


class LocationsForSystemBranh(generics.ListAPIView):
    serializer_class = LocationListSerializersWithBranch
    queryset = Location.objects.all()

    def post(self, request, *args, **kwargs):
        systems = request.data.get('systems', [])
        locations = Location.objects.filter(system__in=systems)

        if locations.count() == 1:
            serializer = LocationListSerializersWithBranch(locations.first())
        else:
            serializer = LocationListSerializersWithBranch(locations, many=True)

        return Response(serializer.data)
