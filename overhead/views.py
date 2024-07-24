from rest_framework import generics
from .models import Overhead
from .serializers import OverheadSerializer
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class OverheadListCreateView(generics.ListCreateAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['overhead', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = Overhead.objects.all()
        serializer = OverheadSerializer(queryset, many=True)
        return Response({'overheads': serializer.data, 'permissions': permissions})


class OverheadRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['overhead', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        overhead = self.get_object()
        overhead_data = self.get_serializer(overhead).data
        return Response({'overhead': overhead_data, 'permissions': permissions})
