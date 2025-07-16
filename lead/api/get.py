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

    # def get_queryset(self):
    #
    #     date_param = self.request.query_params.get('date')
    #     branch_id = self.request.query_params.get('branch_id')
    #
    #     user = self.request.user
    #     if user.groups.filter(name='admin').exists():
    #         operator_id = self.request.query_params.get('operator_id')
    #         if operator_id:
    #             user = CustomUser.objects.get(pk=operator_id)
    #         else:
    #             user = None
    #
    #     today = datetime.now().date()
    #     selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else today
    #     operators = CustomUser.objects.filter(groups__name='operator', branch_id=branch_id)
    #
    #     if selected_date < today:
    #         if user:
    #             operator_lead = OperatorLead.objects.filter(operator=user, date=selected_date).values_list('lead',
    #                                                                                                        flat=True)
    #         else:
    #             operator_lead = OperatorLead.objects.filter(operator__in=operators, date=selected_date).values_list(
    #                 'lead', flat=True)
    #         return LeadCall.objects.filter(
    #             created=selected_date,
    #             deleted=False,
    #             lead__in=operator_lead
    #         )
    #
    #
    #     # 2. Get all operators of this branch
    #     operator_count = operators.count()
    #
    #     # 3. Get today's leads that haven't been given or finished
    #     leads = Lead.objects.filter(
    #         deleted=False,
    #         branch_id=branch_id,
    #         finished=False
    #     )
    #     leads = leads.annotate(
    #         has_leadcall_today=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 delay=selected_date,
    #                 deleted=False
    #             )
    #         ),
    #         has_other_leadcalls=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 deleted=False
    #             ).exclude(delay=selected_date)
    #         ),
    #
    #     ).filter(
    #         Q(has_other_leadcalls=False) | Q(has_leadcall_today=True)
    #     )
    #
    #     leads = list(leads)
    #     total_leads = len(leads)
    #
    #     # 4. Distribute leads to the least-loaded operators
    #     if operator_count > 0 and total_leads > 0:
    #         # Count how many leads each operator already has
    #         operator_lead_counts = defaultdict(int)
    #         for op in operators:
    #             operator_lead_counts[op.id] = OperatorLead.objects.filter(operator=op, date=selected_date).count()
    #
    #         lead_index = 0
    #         while lead_index < total_leads:
    #             # Always pick operator with fewest leads
    #             sorted_operators = sorted(operators, key=lambda op: operator_lead_counts[op.id])
    #             selected_operator = sorted_operators[0]
    #
    #             lead = leads[lead_index]
    #             _, created = OperatorLead.objects.get_or_create(
    #                 lead=lead,
    #                 date=selected_date,
    #                 defaults={
    #                     "operator": selected_operator
    #                 }
    #             )
    #
    #             if created:
    #                 operator_lead_counts[selected_operator.id] += 1
    #
    #             lead_index += 1
    #
    #     if user:
    #         operator_lead = OperatorLead.objects.filter(operator=user, date=selected_date)
    #     else:
    #         operator_lead = OperatorLead.objects.filter(operator__in=operators, date=selected_date)
    #     assigned_leads = Lead.objects.filter(
    #         deleted=False,
    #         branch_id=branch_id,
    #         operatorlead__in=operator_lead,
    #         finished=False
    #     )
    #     assigned_leads = assigned_leads.annotate(
    #
    #         has_other_leadcalls=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 deleted=False,
    #
    #             ).exclude(delay=selected_date)
    #         )
    #
    #     ).filter(
    #         Q(has_other_leadcalls=False)
    #     )
    #     return assigned_leads
    from datetime import datetime
    from collections import defaultdict
    from django.db.models import Q, Exists, OuterRef

    # def get_queryset(self):
    #     date_param = self.request.query_params.get('date')
    #     branch_id = self.request.query_params.get('branch_id')
    #
    #     user = self.request.user
    #     if user.groups.filter(name='admin').exists():
    #         operator_id = self.request.query_params.get('operator_id')
    #         if operator_id:
    #             user = CustomUser.objects.get(pk=operator_id)
    #         else:
    #             user = None
    #
    #     today = datetime.now().date()
    #     selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else today
    #     operators = CustomUser.objects.filter(groups__name='operator', branch_id=branch_id)
    #
    #     # If selected_date is in the past, just return the leads for that day
    #     if selected_date < today:
    #         if user:
    #             operator_lead = OperatorLead.objects.filter(operator=user, date=selected_date).values_list('lead',
    #                                                                                                        flat=True)
    #         else:
    #             operator_lead = OperatorLead.objects.filter(operator__in=operators, date=selected_date).values_list(
    #                 'lead', flat=True)
    #
    #         return LeadCall.objects.filter(
    #             created=selected_date,
    #             deleted=False,
    #             lead__in=operator_lead
    #         )
    #
    #     # Count total leads each operator has (across all dates)
    #     operator_lead_counts = defaultdict(int)
    #     for op in operators:
    #         operator_lead_counts[op.id] = OperatorLead.objects.filter(operator=op, date=selected_date).count()
    #
    #     # Get today's leads (unfinished, not deleted)
    #     all_leads = Lead.objects.filter(
    #         deleted=False,
    #         branch_id=branch_id,
    #         finished=False
    #     )
    #
    #     leads = Lead.objects.filter(
    #         deleted=False,
    #         branch_id=branch_id,
    #         finished=False
    #     ).annotate(
    #         has_other_leadcalls=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 deleted=False
    #             ).exclude(delay=selected_date)
    #         )
    #     ).filter(
    #         Q(has_other_leadcalls=False)
    #     ).order_by('pk')
    #
    #     leads_by_operators = OperatorLead.objects.filter(date=selected_date, operator__in=operators).all()
    #     not_assigned_leads = all_leads.exclude(operatorlead__in=leads_by_operators).filter(finished=False)
    #     print('leads_by_operators', len(leads_by_operators))
    #     print('not_assigned_leads', len(not_assigned_leads))
    #     # Annotate leads with call status
    #     leads = leads.annotate(
    #         has_leadcall_today=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 delay=selected_date,
    #                 deleted=False
    #             )
    #         ),
    #         has_other_leadcalls=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 deleted=False
    #             ).exclude(delay=selected_date)
    #         ),
    #     ).filter(
    #         Q(has_other_leadcalls=False)
    #     )
    #
    #     leads = list(leads)
    #     total_leads = len(leads)
    #
    #     lead_index = 0
    #
    #     leads_to_assign = Lead.objects.filter(
    #         deleted=False,
    #         branch_id=branch_id,
    #         finished=False
    #     ).annotate(
    #         has_other_calls=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 deleted=False
    #             ).exclude(delay=selected_date)
    #         )
    #     ).filter(
    #         has_other_calls=False
    #     )
    #     print('leads_to_assign', len(leads_to_assign))
    #     while lead_index < total_leads:
    #         lead = leads[lead_index]
    #
    #         # Check if lead has previous assignment
    #         previous_assignment = OperatorLead.objects.filter(
    #             lead=lead
    #         ).order_by('-date').first()
    #
    #         if previous_assignment:
    #             operator = previous_assignment.operator
    #         else:
    #             # Pick operator with fewest total leads
    #             sorted_operators = sorted(operators, key=lambda op: operator_lead_counts[op.id])
    #             operator = sorted_operators[0] if sorted_operators else None
    #
    #         # Assign today's lead if not already assigned
    #         if operator:
    #             _, created = OperatorLead.objects.get_or_create(
    #                 lead=lead,
    #                 date=selected_date,
    #                 defaults={"operator": operator}
    #             )
    #
    #             if created:
    #                 operator_lead_counts[operator.id] += 1
    #
    #             lead_index += 1
    #
    #         else:
    #             lead_index += 1
    #
    #     # Fetch the leads assigned for today
    #     if user:
    #         operator_lead = OperatorLead.objects.filter(operator=user, date=selected_date)
    #     else:
    #         operator_lead = OperatorLead.objects.filter(operator__in=operators, date=selected_date)
    #
    #     assigned_leads = Lead.objects.filter(
    #         deleted=False,
    #         branch_id=branch_id,
    #         operatorlead__in=operator_lead,
    #         finished=False
    #     ).annotate(
    #         has_other_leadcalls=Exists(
    #             LeadCall.objects.filter(
    #                 lead=OuterRef('pk'),
    #                 deleted=False
    #             ).exclude(delay=selected_date)
    #         )
    #     ).filter(
    #         Q(has_other_leadcalls=False)
    #     ).order_by('pk')
    from collections import defaultdict
    from datetime import datetime
    from django.db.models import OuterRef, Exists, Q
    from django.utils.timezone import now

    def get_queryset(self):

        date_param = self.request.query_params.get('date')
        branch_id = self.request.query_params.get('branch_id')
        user = self.request.user

        # If admin, allow filtering by operator_id
        if user.groups.filter(name='admin').exists():
            operator_id = self.request.query_params.get('operator_id')
            if operator_id:
                user = CustomUser.objects.get(pk=operator_id)
            else:
                user = None

        today = now().date()
        selected_date = datetime.strptime(date_param, "%Y-%m-%d").date() if date_param else today
        operators = CustomUser.objects.filter(
            branch_id=branch_id,
            customautogroup__group__name='operator',
            customautogroup__deleted=False
        )

        print("operators", len(operators))
        # previous_assignment = OperatorLead.objects.filter(
        #     operator__in=operators,
        #     date=selected_date
        # ).delete()
        # Short-circuit if date is in the past
        if selected_date < today:
            operator_leads = OperatorLead.objects.filter(
                operator=user if user else None,
                date=selected_date
            ).values_list('lead', flat=True)

            return LeadCall.objects.filter(
                created=selected_date,
                deleted=False,
                lead__in=operator_leads
            )

        # 🧮 Operator lead counts for today
        operator_lead_counts = {
            op.id: OperatorLead.objects.filter(operator=op, date=selected_date).count()
            for op in operators
        }
        operators_one = OperatorLead.objects.filter(operator_id=985, date="2025-07-15").order_by('lead')
        print("operators_one", len(operators_one))
        # 🔁 Step 1: Reassign unfinished leads with a previous assignment but no assignment today
        previously_assigned_leads = OperatorLead.objects.filter(
            lead__finished=False
        ).exclude(
            date=selected_date
        ).values('lead_id').distinct()

        leads_missing_today = Lead.objects.filter(
            id__in=[entry['lead_id'] for entry in previously_assigned_leads],
            deleted=False,
            finished=False
        ).exclude(
            operatorlead__date=selected_date
        )
        print("leads_missing_today", len(leads_missing_today))
        operator_ids = []

        for lead in leads_missing_today:
            prev = OperatorLead.objects.filter(lead=lead).order_by('-date').first()
            operator_ids.append(prev.operator.id)
            if prev:
                _, created = OperatorLead.objects.get_or_create(
                    lead=lead,
                    date=selected_date,
                    defaults={'operator': prev.operator}
                )
                if created:
                    operator_lead_counts[prev.operator.id] += 1
        operator_ids = list(set(operator_ids))
        all_leads = Lead.objects.filter(
            branch_id=branch_id,
            deleted=False,
            finished=False
        )
        not_assigned_leads = OperatorLead.objects.filter(~Q(lead__in=all_leads)).values_list('lead', flat=True)
        print("not_assigned_leads", len(not_assigned_leads))
        print("operator_ids", operator_ids)
        print("operator_lead_counts", operator_lead_counts)
        # 🔎 Step 2: Assign new leads that were never assigned or called before (except today)
        leads_to_assign = Lead.objects.filter(
            deleted=False,
            branch_id=branch_id,
            finished=False
        ).annotate(
            has_old_calls=Exists(
                LeadCall.objects.filter(
                    lead=OuterRef('pk'),
                    deleted=False
                ).exclude(delay=selected_date)
            )
        ).filter(
            has_old_calls=False
        ).exclude(
            operatorlead__date=selected_date
        ).order_by('pk')
        print("leads_to_assign", len(leads_to_assign))
        #
        # for lead in leads_to_assign:
        #     sorted_ops = sorted(operators, key=lambda op: operator_lead_counts[op.id])
        #     selected_op = sorted_ops[0] if sorted_ops else None
        #     if selected_op:
        #         _, created = OperatorLead.objects.get_or_create(
        #             lead=lead,
        #             date=selected_date,
        #             defaults={'operator': selected_op}
        #         )
        #         if created:
        #             operator_lead_counts[selected_op.id] += 1

        # 📦 Return today's assigned leads
        today_operator_leads = OperatorLead.objects.filter(
            date=selected_date,
            operator=user if user else None
        )
        print("today_operator_leads", len(today_operator_leads))

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
        print('leads', len(leads))
        return leads

        # return assigned_leads
        # all leads 452

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
            stats = calculate_leadcall_status_stats(selected_date, requests=request, branch_id=branch_id,
                                                    operator_lead=operator_lead)

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
            operators = CustomUser.objects.filter(groups__name='operator', branch_id=branch_id)
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
            stats = calculate_leadcall_status_stats(
                selected_date,
                requests=request,
                branch_id=branch_id,
                operator_lead=operator_lead_qs,
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
