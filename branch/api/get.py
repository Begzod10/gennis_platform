from rest_framework import generics
from branch.serializers import BranchListSerializer
from branch.models import Branch
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class BranchListAPIView(generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['branch', 'location']
        permissions = check_user_permissions(user, table_names)

        queryset = Branch.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = BranchListSerializer(queryset, many=True)
        return Response({'branches': serializer.data, 'permissions': permissions})


class BranchRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['branch', 'location']
        permissions = check_user_permissions(user, table_names)
        create_branches = self.get_object()
        create_branches_data = self.get_serializer(create_branches).data
        return Response({'branches': create_branches_data, 'permissions': permissions})


class BranchForLocations(generics.ListAPIView):
    serializer_class = BranchListSerializer
    queryset = Branch.objects.all()

    def post(self, request, *args, **kwargs):
        locations = request.data.get('locations',[])
        branches = Branch.objects.filter(location__in=locations)
        if branches.count() == 1:
            serializer = BranchListSerializer(branches.first())
        else:
            serializer = BranchListSerializer(branches, many=True)
        return Response(serializer.data)


