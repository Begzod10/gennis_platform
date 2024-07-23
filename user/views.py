import jwt
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from gennis_platform import settings
from .serializers import UserSerializer, UserSalaryListSerializers, CustomTokenObtainPairSerializer
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth
from .models import CustomUser, UserSalaryList


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['customuser', 'branch', 'language', 'auth_group', 'auth_permission']
        permissions = check_user_permissions(user, table_names)

        queryset = CustomUser.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response({'users': serializer.data, 'permissions': permissions})


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['customuser', 'branch', 'language', 'auth_group', 'auth_permission']
        permissions = check_user_permissions(user, table_names)
        user = self.get_object()
        user_data = self.get_serializer(user).data
        return Response({'user': user_data, 'permissions': permissions})


class UserSalaryListListCreateView(generics.ListCreateAPIView):
    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalarylist', 'usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)

        queryset = UserSalaryList.objects.all()
        serializer = UserSalaryListSerializers(queryset, many=True)
        return Response({'usersalarylists': serializer.data, 'permissions': permissions})


class UserSalaryListDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSalaryListSerializers

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalarylist', 'usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)
        user_salary_list = self.get_object()
        user_salary_list_data = self.get_serializer(user_salary_list).data
        return Response({'usersalarylist': user_salary_list_data, 'permissions': permissions})


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
        serializer = UserSerializer(user)
        table_names = ['customuser']
        permissions = check_user_permissions(user, table_names)
        return Response({'user': serializer.data, 'permissions': permissions})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
