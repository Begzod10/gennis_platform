from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth
from user.models import CustomUser, UserSalaryList
from user.serializers import UserSerializerWrite, UserSalaryListSerializers, CustomTokenObtainPairSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerWrite

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['customuser', 'branch', 'language', 'auth_group', 'auth_permission']
        permissions = check_user_permissions(user, table_names)

        queryset = CustomUser.objects.all()
        serializer = UserSerializerWrite(queryset, many=True)
        return Response({'users': serializer.data, 'permissions': permissions})


class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerWrite

    def partial_update(self, request, *args, **kwargs):
        print(request.data)
        return Response('adad')


class UserDestroyView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerWrite


class UserSalaryListCreateView(generics.CreateAPIView):
    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializers


class UserSalaryListUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSalaryListSerializers


class UserSalaryListDestroyView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSalaryListSerializers


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
