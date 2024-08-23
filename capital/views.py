from rest_framework import generics
from .serializers import (CapitalCategorySerializers)
from .models import CapitalCategory
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions

import json


class CreateCapitalCategoryList(generics.ListCreateAPIView):
    queryset = CapitalCategory.objects.all()
    serializer_class = CapitalCategorySerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['capitalcategory']
        permissions = check_user_permissions(user, table_names)

        queryset = CapitalCategory.objects.all()
        serializer = CapitalCategorySerializers(queryset, many=True)
        return Response({'capitalcategorys': serializer.data, 'permissions': permissions})


class CapitalCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CapitalCategory.objects.all()
    serializer_class = CapitalCategorySerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['capitalcategory']
        permissions = check_user_permissions(user, table_names)
        capital_category = self.get_object()
        capital_category_data = self.get_serializer(capital_category).data
        return Response({'capitalcategory': capital_category_data, 'permissions': permissions})

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({'message': 'Capital category deleted successfully'}, status=200)
