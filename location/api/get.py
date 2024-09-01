from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from location.models import Location
from location.serializers import LocationListSerializers, LocationListSerializersWithBranch


class LocationListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Location.objects.all()
    serializer_class = LocationListSerializers

    def get(self, request, *args, **kwargs):
        queryset = Location.objects.all()
        serializer = LocationListSerializers(queryset, many=True)
        return Response(serializer.data)


class LocationRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Location.objects.all()
    serializer_class = LocationListSerializers

    def retrieve(self, request, *args, **kwargs):
        locations = self.get_object()
        location_data = self.get_serializer(locations).data
        return Response(location_data)


class LocationsForSystem(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
