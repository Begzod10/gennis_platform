from datetime import datetime

from django.db.models import OuterRef, Exists
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date

from lead.models import Lead, LeadCall
from lead.serializers import LeadListSerializer, LeadCallListSerializer, LeadCallSerializer, LeadSerializer
from lead.utils import calculate_leadcall_status_stats


class LeadListAPIView(generics.ListAPIView):
    def get_serializer_class(self):
        date_param = self.request.query_params.get('date')
        today = timezone.now().date()

        if date_param:
            try:
                selected_date = datetime.strptime(date_param, "%Y-%m-%d").date()
                if selected_date > today:
                    raise ValidationError("Kelajak sanasi bilan so‘rov yuborish mumkin emas.")
                return LeadCallListSerializer if selected_date < today else LeadListSerializer
            except ValueError:
                raise ValidationError("Sana formati noto‘g‘ri. Format: YYYY-MM-DD")
        return LeadListSerializer

    def get_queryset(self):
        date_param = self.request.query_params.get('date')
        # branch_id = self.request.query_params.get('branch_id')
        today = timezone.now().date()
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else today

        if selected_date < today:
            return LeadCall.objects.filter(
                created=selected_date,
                deleted=False
            )

        # leads = Lead.objects.filter(deleted=False, branch_id=branch_id)
        leads = Lead.objects.filter(deleted=False)
        leads = leads.annotate(
            has_leadcall_today=Exists(
                LeadCall.objects.filter(
                    lead=OuterRef('pk'),
                    delay=selected_date,
                    deleted=False
                )
            ),
            has_other_leadcalls=Exists(
                LeadCall.objects.filter(
                    lead=OuterRef('pk'),
                    deleted=False
                ).exclude(delay=selected_date)
            )
        ).filter(
            Q(has_other_leadcalls=False) | Q(has_leadcall_today=True)
        )

        return leads

    def list(self, request, *args, **kwargs):
        date_param = request.query_params.get('date')
        # branch_id = request.query_params.get('branch_id')
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else None

        queryset = self.get_queryset()

        # if branch_id:
        #     queryset = queryset.filter(branch_id=branch_id)  # or branch__id=branch_id if it's a related model

        serializer = self.get_serializer(queryset, many=True)

        # stats = calculate_leadcall_status_stats(selected_date, requests=request, branch_id=branch_id)
        stats = calculate_leadcall_status_stats(selected_date, requests=request)

        return Response({
            "data": serializer.data,
            **stats
        })


class LeadRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadListSerializer

    def retrieve(self, request, *args, **kwargs):
        lead = self.get_object()
        lead_data = self.get_serializer(lead).data
        return Response(lead_data)


class LeadCallListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallListSerializer

    def get_queryset(self):
        queryset = LeadCall.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        lead_id = self.request.query_params.get('lead_id', None)
        if lead_id is not None:
            queryset = queryset.filter(lead_id=lead_id)

        serializer = LeadCallListSerializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):

        queryset = LeadCall.objects.all()
        serializer = LeadCallListSerializer(queryset, many=True)
        return Response(serializer.data)


class LeadCallRetrieveAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer

    def list(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            lead_call = LeadCall.objects.filter(lead_id=pk, status=False).all()
        except LeadCall.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LeadCallSerializer(lead_call, many=True)
        return Response(serializer.data)


class LeadCallTodayListView(generics.ListAPIView):
    serializer_class = LeadListSerializer

    def get_queryset(self):
        today = date.today()
        # branch_id = self.request.query_params.get('branch_id')
        # leadcalls_today = LeadCall.objects.filter(created=today, branch_id=branch_id)
        leadcalls_today = LeadCall.objects.filter(created=today)
        lead_ids = leadcalls_today.values_list('lead', flat=True)
        return Lead.objects.filter(id__in=lead_ids)

    def list(self, request, *args, **kwargs):
        today = timezone.now().date()
        branch_id = request.query_params.get('branch_id')
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        stats = calculate_leadcall_status_stats(today, requests=request)

        return Response({
            "data": serializer.data,
            **stats
        })
