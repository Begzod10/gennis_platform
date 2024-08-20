from rest_framework import generics
from rest_framework.response import Response

from overhead.models import Overhead
from overhead.serializers import OverheadSerializerGet
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth


class OverheadListView(generics.ListAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerGet

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['overhead', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = Overhead.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = OverheadSerializerGet(queryset, many=True)
        return Response({'overheads': serializer.data, 'permissions': permissions})


class OverheadRetrieveView(generics.RetrieveAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerGet

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['overhead', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        overhead = self.get_object()
        overhead_data = self.get_serializer(overhead).data
        return Response({'overhead': overhead_data, 'permissions': permissions})
