import jwt
from django.db.models.query import QuerySet as queryset
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gennis_platform import settings
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth
from user.models import CustomUser, UserSalaryList
from user.serializers import UserSerializerRead, UserSalaryListSerializersRead, Employeers, UserSalarySerializers, \
    UserSalary, CustomAutoGroup


class UserListCreateView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerRead

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['customuser', 'branch', 'language', 'auth_group', 'auth_permission']
        permissions = check_user_permissions(user, table_names)

        queryset = CustomUser.objects.all()
        serializer = UserSerializerRead(queryset, many=True)
        return Response({'users': serializer.data, 'permissions': permissions})


class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerRead

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['customuser', 'branch', 'language', 'auth_group', 'auth_permission']
        permissions = check_user_permissions(user, table_names)
        user = self.get_object()
        user_data = self.get_serializer(user).data
        return Response({'user': user_data, 'permissions': permissions})


class UserSalaryListListView(generics.ListAPIView):
    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializersRead

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalarylist', 'usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)

        queryset = UserSalaryList.objects.all()
        serializer = UserSalaryListSerializersRead(queryset, many=True)
        return Response({'usersalarylists': serializer.data, 'permissions': permissions})


class UserSalaryListDetailView(generics.RetrieveAPIView):
    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializersRead

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalarylist', 'usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)
        user_salary_list = self.get_object()
        user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        return Response({'usersalarylist': user_salary_list_data, 'permissions': permissions})

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return UserSalaryList.objects.filter(user_salary_id=user_id).all()
        except UserSalaryList.DoesNotExist:
            raise NotFound('UserSalary not found for the given user_id')


class UserMe(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'error': 'Authorization header is missing'}, status=400)
        token = auth_header.split(' ')[1]

        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get('user_id')
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        serializer = UserSerializerRead(user)
        table_names = ['customuser']
        permissions = check_user_permissions(user, table_names)
        return Response({'user': serializer.data, 'permissions': permissions})


class EmployeersListView(generics.ListAPIView):
    queryset = CustomAutoGroup.objects.all()
    serializer_class = Employeers


class EmployerRetrieveView(generics.RetrieveAPIView):
    queryset = CustomAutoGroup.objects.all()

    serializer_class = Employeers


class UserSalaryMonthView(generics.RetrieveAPIView):
    queryset = UserSalary.objects.all()
    serializer_class = UserSalarySerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)
        user_salary_list = self.get_object()
        if isinstance(user_salary_list, queryset):
            user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        else:
            user_salary_list_data = self.get_serializer(user_salary_list).data
        return Response({'usersalary': user_salary_list_data, 'permissions': permissions})

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return UserSalary.objects.filter(user_id=user_id).all()
        except UserSalary.DoesNotExist:
            raise NotFound('UserSalary not found for the given user_id')
