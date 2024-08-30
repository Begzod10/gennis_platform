import jwt
import requests
from django.db.models.query import QuerySet as queryset
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gennis_platform import settings
from gennis_platform.settings import classroom_server
from permissions.functions.CheckUserPermissions import check_user_permissions
from permissions.response import CustomResponseMixin, QueryParamFilterMixin
from subjects.serializers import SubjectSerializer, Subject
from user.functions.functions import check_auth
from user.models import CustomUser, UserSalaryList
from user.serializers import UserSerializerRead, UserSalaryListSerializersRead, Employeers, UserSalary, CustomAutoGroup, \
    UserSalarySerializersRead


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
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
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
    queryset = UserSalaryList.objects.filter(deleted=False).all()
    serializer_class = UserSalaryListSerializersRead

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalarylist', 'usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)

        queryset = UserSalaryList.objects.filter(deleted=False).all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = UserSalaryListSerializersRead(queryset, many=True)
        return Response({'usersalarylists': serializer.data, 'permissions': permissions})


class DeletedUserSalaryListListView(generics.ListAPIView):
    queryset = UserSalaryList.objects.filter(deleted=True).all()
    serializer_class = UserSalaryListSerializersRead

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalarylist', 'usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)

        queryset = UserSalaryList.objects.filter(deleted=True).all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = UserSalaryListSerializersRead(queryset, many=True)
        return Response({'usersalarylists': serializer.data, 'permissions': permissions})


class UserSalaryListDetailView(QueryParamFilterMixin, CustomResponseMixin,generics.RetrieveAPIView):
    filter_mappings = {
        'status': 'deleted',
    }
    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializersRead

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['usersalarylist', 'usersalary', 'customautogroup', 'paymenttypes', 'branch', 'customuser']
        permissions = check_user_permissions(user, table_names)
        user_salary_list = self.filter_queryset(self.get_object())
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


class EmployeersListView(QueryParamFilterMixin, CustomResponseMixin, generics.ListAPIView):
    filter_mappings = {
        'age': 'user__birth_date',
        'language': 'user__language_id',
        'branch': 'user__branch__id',
        'job': 'group__id'
    }

    queryset = CustomAutoGroup.objects.all()
    serializer_class = Employeers

    def get_queryset(self):
        queryset = CustomAutoGroup.objects.all()
        queryset = self.filter_queryset(queryset)

        return queryset


class EmployerRetrieveView(generics.RetrieveAPIView):
    queryset = CustomAutoGroup.objects.all()

    serializer_class = Employeers


class UserSalaryMonthView(generics.RetrieveAPIView):
    queryset = UserSalary.objects.all()
    serializer_class = UserSalarySerializersRead

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


class UsersWithJob(APIView):
    def get(self, request, *args, **kwargs):
        queryset = CustomUser.objects.all()
        serializer = UserSerializerRead(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        job = request.data['job']
        if not job:
            return Response({"error": "Job parameter is required."}, status=400)

        jobs = CustomUser.objects.filter(groups__id=job)
        if jobs.exists():
            if jobs.count() == 1:
                serializer = UserSerializerRead(jobs.first())
            else:
                serializer = UserSerializerRead(jobs, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No users found with the specified job."}, status=404)


class SetObserverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)

        user.observer = not user.observer
        user.save()

        action = "given" if user.observer else "taken"
        response_message = f"Permission was {action}"

        requests.get(f"{classroom_server}/api/set_observer/{user.id}")

        # Return a response
        return Response({
            "msg": response_message,
            "success": True
        })


class GetUserAPIView(APIView):

    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(user_id=request.user.id)
        user_serializer = UserSerializerRead(user)

        subjects = Subject.objects.all().order_by('id')
        subject_list = [SubjectSerializer(sub).data for sub in subjects]

        jwt_payload_handler = settings.SIMPLE_JWT['JWT_PAYLOAD_HANDLER']
        jwt_encode_handler = settings.SIMPLE_JWT['JWT_ENCODE_HANDLER']

        payload = jwt_payload_handler(request.user)
        access_token = jwt_encode_handler(payload)
        refresh_token = jwt_encode_handler(payload)

        response_data = {
            "data": user_serializer.data,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "subject_list": subject_list,
        }

        return Response(response_data)
