import pprint
from collections import defaultdict
from datetime import date
from datetime import datetime

from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from students.models import Branch
from lead.models import Lead, LeadCall, OperatorLead
from lead.serializers import LeadListSerializer, LeadCallListSerializer, LeadCallSerializer, LeadSerializer
from lead.utils import calculate_leadcall_status_stats
from user.models import CustomUser


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
        get_branch = Branch.objects.get(id=8)

        date_param = self.request.query_params.get('date')
        branch_id = self.request.query_params.get('branch_id')

        user = self.request.user
        today = timezone.now().date()
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else today
        OperatorLead.objects.filter(date=selected_date).delete()
        Lead.objects.filter(branch=get_branch).update(given_to_operator=False)
        # 1. If date is in the past, return LeadCalls
        if selected_date < today:
            return LeadCall.objects.filter(
                created=selected_date,
                deleted=False
            )

        # 2. Get all operators of this branch
        operators = CustomUser.objects.filter(groups__name='operator', branch_id=branch_id)
        operator_count = operators.count()

        # 3. Get today's leads that haven't been given or finished
        leads = Lead.objects.filter(
            deleted=False,
            branch_id=branch_id,
            given_to_operator=False,
            finished=False
        )
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

        leads = list(leads)
        total_leads = len(leads)

        # 4. Distribute leads to the least-loaded operators
        if operator_count > 0 and total_leads > 0:
            # Count how many leads each operator already has
            operator_lead_counts = defaultdict(int)
            for op in operators:
                operator_lead_counts[op.id] = OperatorLead.objects.filter(operator=op, date=selected_date).count()

            lead_index = 0
            while lead_index < total_leads:
                # Always pick operator with fewest leads
                sorted_operators = sorted(operators, key=lambda op: operator_lead_counts[op.id])
                selected_operator = sorted_operators[0]

                lead = leads[lead_index]
                _, created = OperatorLead.objects.get_or_create(
                    operator=selected_operator,
                    lead=lead,
                    date=selected_date
                )

                if created:
                    lead.given_to_operator = True
                    lead.save()
                    operator_lead_counts[selected_operator.id] += 1

                lead_index += 1

        # 5. Return only this operator's leads for today
        operator_lead = OperatorLead.objects.filter(operator=user, date=selected_date)
        assigned_leads = Lead.objects.filter(
            deleted=False,
            given_to_operator=True,
            branch_id=branch_id,
            operatorlead__in=operator_lead,
            finished=False
        )
        return assigned_leads, [op.id for op in operators]

    def list(self, request, *args, **kwargs):
        date_param = request.query_params.get('date')
        branch_id = request.query_params.get('branch_id')
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else None

        queryset, operators = self.get_queryset()
        # if branch_id:
        #     queryset = queryset.filter(branch_id=branch_id)  # or branch__id=branch_id if it's a related model

        serializer = self.get_serializer(queryset, many=True)
        user = request.user
        operator_lead = OperatorLead.objects.filter(operator=user, date=selected_date)
        stats = calculate_leadcall_status_stats(selected_date, requests=request, branch_id=branch_id,
                                                operator_lead=operator_lead)

        return Response({
            "data": serializer.data,
            "operators": operators,
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
            lead_call = LeadCall.objects.filter(lead_id=pk).all()
        except LeadCall.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = LeadCallSerializer(lead_call, many=True)
        get_lead = Lead.objects.filter(pk=pk).first()
        return Response({"history": serializer.data, "lead": LeadSerializer(get_lead).data},
                        status=status.HTTP_200_OK)


class LeadCallTodayListView(generics.ListAPIView):
    serializer_class = LeadListSerializer

    def get_queryset(self):
        today = date.today()
        user = self.request.user

        # branch_id = self.request.query_params.get('branch_id')
        # leadcalls_today = LeadCall.objects.filter(created=today, branch_id=branch_id)
        leadcalls_today = LeadCall.objects.filter(created=today)
        lead_ids = leadcalls_today.values_list('lead', flat=True)
        return Lead.objects.filter(id__in=lead_ids)

    def list(self, request, *args, **kwargs):
        today = timezone.now().date()
        user = request.user
        branch_id = request.query_params.get('branch_id')
        operator_lead = OperatorLead.objects.filter(operator=user, date=today)
        queryset = self.get_queryset()
        queryset = queryset.filter(branch_id=branch_id, given_to_operator=True, operatorlead__in=operator_lead)
        serializer = self.get_serializer(queryset, many=True)
        stats = calculate_leadcall_status_stats(today, requests=request, branch_id=branch_id,
                                                operator_lead=operator_lead)

        return Response({
            "data": serializer.data,
            **stats
        })
