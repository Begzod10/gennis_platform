from rest_framework import generics
from .serializers import (ClassTypesSerializers, ClassColorsSerializers, ClassNumberSerializers, ClassCoinSerializers,
                          StudentCoinSerializers, CoinInfoSerializers)
from .models import ClassNumber, ClassTypes, ClassColors, ClassCoin, CoinInfo, StudentCoin
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class CreateClassCoinList(generics.ListCreateAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classcoin', 'group']
        permissions = check_user_permissions(user, table_names)

        queryset = ClassCoin.objects.all()
        serializer = ClassCoinSerializers(queryset, many=True)
        return Response({'classcoins': serializer.data, 'permissions': permissions})


class ClassCoinRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classcoin', 'group']
        permissions = check_user_permissions(user, table_names)
        class_coin = self.get_object()
        class_coin_data = self.get_serializer(class_coin).data
        return Response({'classcoin': class_coin_data, 'permissions': permissions})


class CreateCoinInfoList(generics.ListCreateAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['coininfo', 'classcoin']
        permissions = check_user_permissions(user, table_names)

        queryset = CoinInfo.objects.all()
        serializer = CoinInfoSerializers(queryset, many=True)
        return Response({'coininfos': serializer.data, 'permissions': permissions})


class CoinInfoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['coininfo', 'classcoin']
        permissions = check_user_permissions(user, table_names)
        coininfo = self.get_object()
        coininfo_data = self.get_serializer(coininfo).data
        return Response({'coininfo': coininfo_data, 'permissions': permissions})


class CreateStudentCoinList(generics.ListCreateAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentcoin', 'classcoin', 'student']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentCoin.objects.all()
        serializer = StudentCoinSerializers(queryset, many=True)
        return Response({'studentcoins': serializer.data, 'permissions': permissions})


class StudentCoinRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentcoin', 'classcoin', 'student']
        permissions = check_user_permissions(user, table_names)
        student_coin = self.get_object()
        student_coin_data = self.get_serializer(student_coin).data
        return Response({'studentcoin': student_coin_data, 'permissions': permissions})


class CreateClassNumberList(generics.ListCreateAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classnumber', 'classtypes', 'subjects']
        permissions = check_user_permissions(user, table_names)

        queryset = ClassNumber.objects.all()
        serializer = ClassNumberSerializers(queryset, many=True)
        return Response({'classnumbers': serializer.data, 'permissions': permissions})


class ClassNumberRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classnumber', 'classtypes', 'subjects']
        permissions = check_user_permissions(user, table_names)
        class_number = self.get_object()
        class_number_data = self.get_serializer(class_number).data
        return Response({'classnumber': class_number_data, 'permissions': permissions})


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
