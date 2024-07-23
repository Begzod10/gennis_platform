from rest_framework import generics
from .serializers import (ClassTypesSerializers, ClassColorsSerializers, ClassNumberSerializers, ClassCoinSerializers,
                          StudentCoinSerializers, CoinInfoSerializers)
from .models import ClassNumber, ClassTypes, ClassColors, ClassCoin, CoinInfo, StudentCoin
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class CreateClassColorsList(generics.ListCreateAPIView):
    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classcolors']
        permissions = check_user_permissions(user, table_names)

        queryset = ClassColors.objects.all()
        serializer = ClassColorsSerializers(queryset, many=True)
        return Response({'classcolors': serializer.data, 'permissions': permissions})


class ClassColorsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classcolors']
        permissions = check_user_permissions(user, table_names)
        class_colors = self.get_object()
        class_colors_data = self.get_serializer(class_colors).data
        return Response({'class_colors': class_colors_data, 'permissions': permissions})


class CreateClassTypesList(generics.ListCreateAPIView):
    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classtypes']
        permissions = check_user_permissions(user, table_names)

        queryset = ClassTypes.objects.all()
        serializer = ClassTypesSerializers(queryset, many=True)
        return Response({'classtypes': serializer.data, 'permissions': permissions})


class ClassTypesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classtypes']
        permissions = check_user_permissions(user, table_names)
        class_types = self.get_object()
        class_types_data = self.get_serializer(class_types).data
        return Response({'classtypes': class_types_data, 'permissions': permissions})
