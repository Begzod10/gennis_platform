from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from branch.models import Branch, Location
from branch.serializers import BranchListSerializer


class BranchListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Branch.objects.filter(location__system__name='school').all()
    serializer_class = BranchListSerializer

    def get(self, request, *args, **kwargs):
        queryset = Branch.objects.filter(location__system__name='school').all()
        location_id = self.request.query_params.get('location_id', None)

        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = BranchListSerializer(queryset, many=True)
        return Response(serializer.data)


class BranchListFilterAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    queryset = Branch.objects.all()
    serializer_class = BranchListSerializer

    def get(self, request, *args, **kwargs):
        locations = Location.objects.filter(system__name='school').all()
        queryset = Branch.objects.filter(location__in=locations).all().exclude(name='Gazalkent').exclude(name='Test')
        serializer = BranchListSerializer(queryset, many=True)
        return Response(serializer.data)


class BranchRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Branch.objects.all()
    serializer_class = BranchListSerializer

    def retrieve(self, request, *args, **kwargs):
        create_branches = self.get_object()
        create_branches_data = self.get_serializer(create_branches).data
        return Response(create_branches_data)


class BranchForLocations(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = BranchListSerializer
    queryset = Branch.objects.all()

    def post(self, request, *args, **kwargs):
        locations = request.data.get('locations', [])
        branches = Branch.objects.filter(location__in=locations)
        if branches.count() == 1:
            serializer = BranchListSerializer(branches.first())
        else:
            serializer = BranchListSerializer(branches, many=True)
        return Response(serializer.data)
