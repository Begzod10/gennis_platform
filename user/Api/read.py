import jwt
import requests
from django.db.models.query import QuerySet as queryset
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status,filters
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from gennis_platform import settings
from gennis_platform.settings import classroom_server
from permissions.response import IsAdminOrIsSelf
from permissions.response import QueryParamFilterMixin
from subjects.serializers import SubjectSerializer, Subject
from user.models import CustomUser, UserSalaryList
from user.serializers import UserSerializerRead, UserSalaryListSerializersRead, Employeers, UserSalary, CustomAutoGroup,UserSalaryListSerializersTotal
from user.seriliazer.employer import EmployerSerializer
from user.seriliazer.employer import UserForOneMonthListSerializer, EmployerSalaryMonths
from ..serialziers_list import UsersWithJobSerializers
from django_filters.rest_framework import DjangoFilterBackend
from user.filters import UserSalaryListFilter
from django.db.models import Sum
from permissions.response import CustomPagination

class UserListCreateView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerRead

    def get(self, request, *args, **kwargs):
        queryset = CustomUser.objects.all()
        serializer = UserSerializerRead(queryset, many=True)
        return Response(serializer.data)


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrIsSelf]

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerRead

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        user_data = self.get_serializer(user).data
        return Response(user_data)


class UserSalaryListListView(QueryParamFilterMixin, generics.ListAPIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    permission_classes = [IsAuthenticated]
    search_fields = ['user__name', 'user__surname', 'user__username']

    queryset = UserSalaryList.objects.filter(deleted=False).all()
    serializer_class = UserSalaryListSerializersTotal
    filterset_class = UserSalaryListFilter
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        data = [
            {
                "name": "Total Amount",
                "totalPayment": queryset.aggregate(total_sum=Sum('salary'))['total_sum'] or 0,
                "totalPaymentCount": queryset.count(),
                "type": "amount"
            },
            {
                "name": "Cash Payments",
                "totalPayment":
                    queryset.filter(payment_types__name__iexact='Cash').aggregate(total_sum=Sum('salary'))[
                        'total_sum'] or 0,
                "totalPaymentCount": queryset.filter(payment_types__name__iexact='Cash').count(),
                "type": "cash"
            },
            {
                "name": "Click Payments",
                "totalPayment":
                    queryset.filter(payment_types__name__iexact="Click").aggregate(total_sum=Sum('salary'))[
                        'total_sum'] or 0,
                "totalPaymentCount": queryset.filter(payment_types__name__iexact="Click").count(),
                "type": "click"
            },
            {
                "name": "Bank Transfers",
                "totalPayment":
                    queryset.filter(payment_types__name__iexact="Bank").aggregate(total_sum=Sum('salary'))[
                        'total_sum'] or 0,
                "totalPaymentCount": queryset.filter(payment_types__name__iexact="Bank").count(),
                "type": "bank"
            },
        ]

        return self.get_paginated_response({
            'data': serializer.data,
            'totalCount': data
        })


class DeletedUserSalaryListListView(QueryParamFilterMixin, generics.ListAPIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    permission_classes = [IsAuthenticated]
    serializer_class = UserSalaryListSerializersRead

    def get_queryset(self):
        queryset = UserSalaryList.objects.filter(deleted=True)
        return self.filter_queryset(queryset)


class UserSalaryListDetailView(QueryParamFilterMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        'status': 'deleted',
    }
    queryset = UserSalaryList.objects.all()
    serializer_class = UserForOneMonthListSerializer

    def retrieve(self, request, *args, **kwargs):
        get_salary = UserSalary.objects.get(id=self.kwargs.get('pk'))
        salaries = UserSalaryList.objects.filter(user_salary_id=get_salary.id, deleted=False).all()
        total_salary = 0
        for sal in salaries:
            total_salary += sal.salary
        remaining_salary = get_salary.total_salary - total_salary
        get_salary.remaining_salary = remaining_salary
        get_salary.taken_salary = total_salary
        get_salary.save()
        user_salary_list = self.filter_queryset(self.get_object())
        user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        return Response(user_salary_list_data)

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

        return Response(serializer.data)


class EmployerDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CustomAutoGroup.objects.all()
    serializer_class = EmployerSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        return Response(status=status.HTTP_200_OK, data={"msg": "Employer deleted successfully"})


class EmployeersListView(QueryParamFilterMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        'age': 'user__birth_date',
        'language': 'user__language_id',
        'branch': 'user__branch__id',
        'job': 'group__id'
    }

    queryset = CustomAutoGroup.objects.filter(deleted=False).all()
    serializer_class = EmployerSerializer


class EmployerRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = Employeers
    queryset = CustomAutoGroup.objects.filter(deleted=False).all()

    def get_object(self):
        from user.cron import create_user_salary
        employer = super().get_object()
        create_user_salary(employer.user_id)

        return employer


class UserSalaryMonthView(generics.RetrieveAPIView):
    queryset = UserSalary.objects.all()
    serializer_class = EmployerSalaryMonths
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):

        user_salary_list = self.get_object()
        print(user_salary_list, "user_salary_list")
        for user_salary in user_salary_list:
            user_salary.remaining_salary = user_salary.total_salary - user_salary.taken_salary
            user_salary.save()
        if isinstance(user_salary_list, queryset):
            user_salary_list_data = self.get_serializer(user_salary_list, many=True).data
        else:
            user_salary_list_data = self.get_serializer(user_salary_list).data
        return Response(user_salary_list_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        get_employer = CustomAutoGroup.objects.get(id=user_id)
        try:
            return UserSalary.objects.filter(user_id=get_employer.user_id).all()
        except UserSalary.DoesNotExist:
            raise NotFound('UserSalary not found for the given user_id')


class UsersWithJob(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = CustomUser.objects.all()
        serializer = UsersWithJobSerializers(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        job = request.data['job']
        if not job:
            return Response({"error": "Job parameter is required."}, status=400)

        jobs = CustomUser.objects.filter(groups__id=job)
        if jobs.exists():
            if jobs.count() == 1:
                serializer = UsersWithJobSerializers(jobs.first())
            else:
                serializer = UsersWithJobSerializers(jobs, many=True)
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
