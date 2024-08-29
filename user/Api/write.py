from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
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
    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()

        user_salary = instance.user_salary
        user_salary.taken_salary -= instance.salary
        user_salary.remaining_salary += instance.salary
        user_salary.save()

        return Response({"msg": " salary deleted successfully"}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsernameCheck(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        if username:
            try:
                user = CustomUser.objects.get(username=username)
                return Response({'exists': True}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'exists': False}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)
