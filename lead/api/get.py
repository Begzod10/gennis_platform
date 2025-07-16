from collections import defaultdict
from datetime import datetime

from django.db.models import Exists, OuterRef, Q
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lead.models import Lead, LeadCall, OperatorLead
from lead.serializers import LeadListSerializer, LeadCallListSerializer, LeadCallSerializer, LeadSerializer
from lead.utils import calculate_leadcall_status_stats, calculate_all_percentage
from user.models import CustomUser, CustomAutoGroup
from django.utils.timezone import now


class LeadListAPIView(generics.ListAPIView):
    def get_serializer_class(self):
        date_param = self.request.query_params.get('date')
        today = datetime.now().date()

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
        from django.db.models import Q, Count

        date_param = self.request.query_params.get('date')
        branch_id = self.request.query_params.get('branch_id')
        user = self.request.user
        operators = CustomUser.objects.filter(
            branch_id=branch_id,
            customautogroup__group__name='operator',
            customautogroup__deleted=False
        )
        # Handle admin override for operator filtering
        if user.groups.filter(name='admin').exists():
            operator_id = self.request.query_params.get('operator_id')
            if operator_id:
                operator = CustomUser.objects.get(pk=operator_id)
            else:
                operator = operators
        else:
            operator = user
        today = now().date()
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else today



        # Operator lead counts today
        operator_lead_counts = {
            op.id: OperatorLead.objects.filter(operator=op, date=selected_date).count()
            for op in operators
        }

        # Step 1: Reassign unfinished leads from previous days (if not already assigned today)
        previously_assigned_leads = OperatorLead.objects.filter(
            lead__finished=False
        ).exclude(date=selected_date).values('lead_id').distinct()

        leads_missing_today = Lead.objects.filter(
            id__in=[entry['lead_id'] for entry in previously_assigned_leads],
            deleted=False,
            finished=False
        ).exclude(
            operatorlead__date=selected_date
        )

        for lead in leads_missing_today:
            prev = OperatorLead.objects.filter(lead=lead).order_by('-date').first()
            if prev:
                # If the previous operator already has a lead today, pick one with fewer
                preferred_operator = prev.operator
                if preferred_operator.id not in [op.id for op in operators]:
                    continue  # skip if previous operator is not in active list

                conflict = OperatorLead.objects.filter(operator=preferred_operator, date=selected_date).exists()
                if conflict:
                    sorted_ops = sorted(operators, key=lambda op: operator_lead_counts.get(op.id, 0))
                    preferred_operator = sorted_ops[0]

                _, created = OperatorLead.objects.get_or_create(
                    lead=lead,
                    date=selected_date,
                    defaults={'operator': preferred_operator}
                )
                if created:
                    operator_lead_counts[preferred_operator.id] += 1

        # Step 2: Assign completely new leads (never assigned before)
        # All unfinished & undeleted leads in this branch
        all_open_leads = Lead.objects.filter(
            branch_id=branch_id,
            deleted=False,
            finished=False
        )

        # Already assigned leads
        already_assigned_lead_ids = OperatorLead.objects.values_list('lead_id', flat=True).distinct()

        # Unassigned leads
        unassigned_leads = all_open_leads.exclude(id__in=already_assigned_lead_ids)

        # print("finished_leads", Lead.objects.filter(branch_id=branch_id, finished=True).count())
        # print("deleted_leads", Lead.objects.filter(branch_id=branch_id, deleted=True).count())
        # print("unassigned_leads", unassigned_leads.count())

        for lead in unassigned_leads:
            sorted_ops = sorted(operators, key=lambda op: operator_lead_counts.get(op.id, 0))
            selected_op = sorted_ops[0] if sorted_ops else None
            if selected_op:
                _, created = OperatorLead.objects.get_or_create(
                    lead=lead,
                    date=selected_date,
                    defaults={'operator': selected_op}
                )
                if created:
                    operator_lead_counts[selected_op.id] += 1

        # print("operator_lead_counts", operator_lead_counts)

        # Return leads assigned to current user (or selected operator) today
        today_operator_leads = OperatorLead.objects.filter(
            date=selected_date,
            operator__in=operator
        )
        # print("today_operator_leads", today_operator_leads.count())

        leads = Lead.objects.filter(
            deleted=False,
            branch_id=branch_id,
            finished=False,
            operatorlead__in=today_operator_leads
        ).annotate(
            has_old_calls=Exists(
                LeadCall.objects.filter(
                    lead=OuterRef('pk'),
                    deleted=False
                ).exclude(delay=selected_date)
            )
        ).order_by('pk')

        # print("leads", leads.count())

        return leads

    def list(self, request, *args, **kwargs):
        date_param = request.query_params.get('date')
        branch_id = request.query_params.get('branch_id')
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else None

        operators = CustomUser.objects.filter(
            branch_id=branch_id,
            customautogroup__group__name='operator',
            customautogroup__deleted=False
        )

        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        operator_id = self.request.query_params.get('operator_id')
        user = self.request.user  # faqat bitta user
        if user.groups.filter(name='admin').exists():
            if operator_id:
                user = CustomUser.objects.get(pk=operator_id)  # tanlangan operator
            else:
                user = None

        if user:
            operator_lead = OperatorLead.objects.filter(operator=user, date=selected_date)
        else:
            operator_lead = OperatorLead.objects.filter(operator__in=operators, date=selected_date)
        if user is not None:
            stats, leadcall_today_ids = calculate_leadcall_status_stats(selected_date, requests=request,
                                                                        branch_id=branch_id,
                                                                        operator_lead=operator_lead,
                                                                        operator_id=operator_id)
            queryset = self.get_queryset()
            if leadcall_today_ids:
                leadcall_today_ids = list(leadcall_today_ids)
                queryset = queryset.exclude(Q(pk__in=leadcall_today_ids))

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "data": serializer.data,
                "operators": list(operators.values("id", "name", "surname")),
                **stats
            })
        else:
            stats = calculate_all_percentage(selected_date, branch_id)

            return Response({
                "data": serializer.data,
                "operators": list(operators.values("id", "name", "surname")),
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

    def get_selected_date(self):
        """
        Query parametrlardan selected_date ni aniqlash.
        """
        date_param = self.request.query_params.get('date')
        today = datetime.now().date()

        if date_param:
            try:
                selected_date = datetime.strptime(date_param, "%Y-%m-%d").date()
                if selected_date > today:
                    raise ValidationError("Kelajak sanasi bilan so‘rov yuborish mumkin emas.")
                return selected_date
            except ValueError:
                raise ValidationError("Sana formati noto‘g‘ri. Format: YYYY-MM-DD")
        return today

    def get_operator_user(self):
        """
        Agar admin bo‘lsa va operator_id kelgan bo‘lsa, shuni qaytaradi.
        """
        user = self.request.user
        if user.groups.filter(name='admin').exists():
            operator_id = self.request.query_params.get('operator_id')
            if operator_id:
                try:
                    return CustomUser.objects.get(pk=operator_id)
                except CustomUser.DoesNotExist:
                    raise ValidationError("Bunday operator mavjud emas.")
            return None
        return user

    def get_operator_leads(self, operator, date, branch_id):
        """
        OperatorLead querysetini qaytaradi.
        """
        if operator:
            return OperatorLead.objects.filter(operator=operator, date=date)
        else:
            operators = CustomUser.objects.filter(
                branch_id=branch_id,
                customautogroup__group__name='operator',
                customautogroup__deleted=False
            )
            return OperatorLead.objects.filter(operator__in=operators, date=date)

    def get_queryset(self):
        selected_date = self.get_selected_date()
        branch_id = self.request.query_params.get('branch_id')

        operator_user = self.get_operator_user()
        operator_lead_qs = self.get_operator_leads(operator_user, selected_date, branch_id)

        today = datetime.now().date()
        if selected_date < today:
            operator_lead_ids = operator_lead_qs.values_list('lead', flat=True)
            return LeadCall.objects.filter(
                created=selected_date,
                deleted=False,
                lead__in=operator_lead_ids,
            )
        leadcalls_today = LeadCall.objects.filter(created=selected_date, deleted=False, branch_id=branch_id)
        lead_ids = leadcalls_today.values_list('lead', flat=True)

        leads = Lead.objects.filter(
            id__in=lead_ids,
            branch_id=branch_id,
            operatorlead__in=operator_lead_qs,
            deleted=False,
        )

        return leads

    def get_serializer_class(self):
        selected_date = self.get_selected_date()
        today = datetime.now().date()

        if selected_date < today:
            return LeadCallListSerializer
        return LeadListSerializer

    def list(self, request, *args, **kwargs):
        selected_date = self.get_selected_date()
        operator_user = self.get_operator_user()

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        branch_id = request.query_params.get('branch_id')
        operator_lead_qs = self.get_operator_leads(operator_user, selected_date, branch_id)
        if operator_user:
            stats, _ = calculate_leadcall_status_stats(
                selected_date,
                requests=request,
                branch_id=branch_id,
                operator_lead=operator_lead_qs,
                operator_id=operator_user.id
            )
        else:
            stats = calculate_all_percentage(selected_date, branch_id)

        return Response({
            "data": serializer.data,
            **stats
        })


class OperatorsListView(generics.ListAPIView):

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch_id')
        operators = CustomUser.objects.filter(
            branch_id=branch_id,
            customautogroup__group__name='operator',
            customautogroup__deleted=False
        )
        return operators

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for user in queryset:
            data.append({
                "id": user.id,
                "name": user.name + " " + user.surname

            })

        return Response(data)


class LeadsByBranchListView(generics.ListAPIView):
    serializer_class = LeadListSerializer

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch_id')
        date = self.request.query_params.get('date')
        return Lead.objects.filter(branch_id=branch_id, created=date)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        lead_count = queryset.count()
        return Response({
            "data": serializer.data,
            "lead_count": lead_count
        })
