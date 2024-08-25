from datetime import timedelta

from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from overhead.models import Overhead, OverheadType
from overhead.serializers import OverheadSerializerGet, OverheadSerializerGetTYpe, MonthDaysSerializer
from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth


class OverheadListView(generics.ListAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerGet

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['overhead', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = Overhead.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(deleted=status)
        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = OverheadSerializerGet(queryset, many=True)
        return Response({'overheads': serializer.data, 'permissions': permissions})


class OverheadTYpeListView(generics.ListAPIView):
    queryset = OverheadType.objects.all()
    serializer_class = OverheadSerializerGetTYpe

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['OverheadType', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = OverheadType.objects.all()
        serializer = OverheadSerializerGetTYpe(queryset, many=True)
        return Response({'overheads': serializer.data, 'permissions': permissions})


class OverheadRetrieveView(generics.RetrieveAPIView):
    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerGet

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['overhead', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)
        overhead = self.get_object()
        overhead_data = self.get_serializer(overhead).data
        return Response({'overhead': overhead_data, 'permissions': permissions})


class MonthDaysView(APIView):
    def get(self, request, format=None):
        try:
            today = timezone.localtime().date()

            current_month_name = today.strftime('%b')
            current_month_value = today.strftime('%m')
            start_of_current_month = today.replace(day=1)
            days_in_current_month = [start_of_current_month + timedelta(days=i) for i in
                                     range((today - start_of_current_month).days + 1)]
            first_of_this_month = today.replace(day=1)
            last_day_of_last_month = first_of_this_month - timedelta(days=1)
            last_month_name = last_day_of_last_month.strftime('%b')
            last_month_value = last_day_of_last_month.strftime('%m')
            start_of_last_month = last_day_of_last_month.replace(day=1)
            days_in_last_month = [start_of_last_month + timedelta(days=i) for i in
                                  range((last_day_of_last_month - start_of_last_month).days + 1)]

            response_data = [
                {
                    "days": [day.day for day in days_in_current_month],
                    "name": current_month_name,
                    "value": current_month_value
                },
                {
                    "days": [day.day for day in days_in_last_month],
                    "name": last_month_name,
                    "value": last_month_value
                }
            ]

            serializer = MonthDaysSerializer(response_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
