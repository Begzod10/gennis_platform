from rest_framework import generics
from class_.serializers import (ClassCoinListSerializers, CoinInfoListSerializers, StudentCoinListSerializers,
                                ClassNumberListSerializers)
from class_.models import ClassNumber, ClassCoin, CoinInfo, StudentCoin
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class ClassNumberRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classnumber', 'classtypes', 'subjects']
        permissions = check_user_permissions(user, table_names)
        class_number = self.get_object()
        class_number_data = self.get_serializer(class_number).data
        return Response({'classnumber': class_number_data, 'permissions': permissions})


class StudentCoinRetrieveAPIView(generics.RetrieveAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentcoin', 'classcoin', 'student']
        permissions = check_user_permissions(user, table_names)
        student_coin = self.get_object()
        student_coin_data = self.get_serializer(student_coin).data
        return Response({'studentcoin': student_coin_data, 'permissions': permissions})


class CoinInfoRetrieveAPIView(generics.RetrieveAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['coininfo', 'classcoin']
        permissions = check_user_permissions(user, table_names)
        coininfo = self.get_object()
        coininfo_data = self.get_serializer(coininfo).data
        return Response({'coininfo': coininfo_data, 'permissions': permissions})


class ClassCoinRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classcoin', 'group']
        permissions = check_user_permissions(user, table_names)
        class_coin = self.get_object()
        class_coin_data = self.get_serializer(class_coin).data
        return Response({'classcoin': class_coin_data, 'permissions': permissions})


class ClassCoinListView(generics.ListAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classcoin', 'group']
        permissions = check_user_permissions(user, table_names)

        queryset = ClassCoin.objects.all()
        serializer = ClassCoinListSerializers(queryset, many=True)
        return Response({'classcoins': serializer.data, 'permissions': permissions})


class CoinInfoListView(generics.ListAPIView):
    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['coininfo', 'classcoin']
        permissions = check_user_permissions(user, table_names)

        queryset = CoinInfo.objects.all()
        serializer = CoinInfoListSerializers(queryset, many=True)
        return Response({'coininfos': serializer.data, 'permissions': permissions})


class StudentCoinListView(generics.ListAPIView):
    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentcoin', 'classcoin', 'student']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentCoin.objects.all()
        serializer = StudentCoinListSerializers(queryset, many=True)
        return Response({'studentcoins': serializer.data, 'permissions': permissions})


class ClassNumberListView(generics.ListAPIView):
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['classnumber', 'classtypes', 'subjects']
        permissions = check_user_permissions(user, table_names)

        queryset = ClassNumber.objects.all()
        serializer = ClassNumberListSerializers(queryset, many=True)
        return Response({'classnumbers': serializer.data, 'permissions': permissions})
