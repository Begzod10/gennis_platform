from datetime import timedelta

from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from overhead.models import Overhead, OverheadType
from overhead.serializers import OverheadSerializerGet, OverheadSerializerGetTYpe, MonthDaysSerializer


class OverheadListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerGet

    def get(self, request, *args, **kwargs):

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
        return Response(serializer.data)


class OverheadTYpeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = OverheadType.objects.all()
    serializer_class = OverheadSerializerGetTYpe

    def get(self, request, *args, **kwargs):
        queryset = OverheadType.objects.all()
        serializer = OverheadSerializerGetTYpe(queryset, many=True)
        return Response(serializer.data)


class OverheadRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Overhead.objects.all()
    serializer_class = OverheadSerializerGet

    def retrieve(self, request, *args, **kwargs):
        overhead = self.get_object()
        overhead_data = self.get_serializer(overhead).data
        return Response(overhead_data)


class MonthDaysView(APIView):
    permission_classes = [IsAuthenticated]

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
