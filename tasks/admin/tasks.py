from django.utils.timezone import now
from django.db.models import OuterRef, Exists, Subquery
from django.db.models import Count, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from attendances.models import AttendancePerMonth
from students.models import CallLog, DeletedStudent
from lead.models import Lead


class DebtorsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch')

        # O'quv yili boshini hisoblash
        if today.month >= 9:  # sentabr-dekabr
            study_year_start = today.replace(month=9, day=1)
        else:  # yanvar-iyun
            study_year_start = today.replace(year=today.year - 1, month=9, day=1)

        base_qs = AttendancePerMonth.objects.filter(
            month_date__gte=study_year_start,  # o'quv yili boshidan
            month_date__lte=today,
            status=False
        ).annotate(
            is_deleted=Exists(
                DeletedStudent.objects.filter(
                    student_id=OuterRef('student_id'),
                    deleted=True
                )
            )
        ).filter(is_deleted=False)

        if branch_id:
            base_qs = base_qs.filter(student__user__branch_id=branch_id)

        last_call = CallLog.objects.filter(
            student=OuterRef('student')
        ).order_by('-created_at')

        debts = (
            base_qs
            .select_related('student__user')
            .values(
                'student',
                'student__user__name',
                'student__user__surname',
                'student__user__phone',
                'student__parents_number',
                "student__user__branch_id"
            )
            .annotate(
                months_count=Count('id'),
                total_debt=Sum('remaining_debt'),
                last_next_call_date=Subquery(last_call.values('next_call_date')[:1]),
            )
        )

        result = []
        for item in debts:
            next_call = item['last_next_call_date']
            if next_call and next_call > today:
                continue

            months = item['months_count']
            color = 'red' if months >= 2 else 'yellow'

            result.append({
                "student_id": item['student'],
                "full_name": f"{item['student__user__name']} {item['student__user__surname']}",
                "phone": item['student__user__phone'],
                "parent_phone": item['student__parents_number'],
                "debt": item['total_debt'] or 0,
                "months_count": months,
                "color": color,
                "branch": item['student__user__branch_id']
            })

        return Response(result)


class LeadsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch')

        base_qs = Lead.objects.filter(
            deleted=False,
            finished=False
        )

        if branch_id:
            base_qs = base_qs.filter(branch_id=branch_id)

        last_call = CallLog.objects.filter(
            lead=OuterRef('pk')
        ).order_by('-created_at')

        leads = base_qs.annotate(
            last_next_call_date=Subquery(last_call.values('next_call_date')[:1]),
            last_called_at=Subquery(last_call.values('created_at')[:1]),
            last_status=Subquery(last_call.values('status')[:1]),
            call_count=Count('calllog'),
        )

        result = []
        for lead in leads:
            next_call = lead.last_next_call_date
            if next_call and next_call > today:
                continue  # hali vaqti kelmagan

            result.append({
                "lead_id": lead.id,
                "full_name": lead.name,
                "phone": lead.phone,
                "branch_id": lead.branch_id,
                "call_count": lead.call_count,
                "last_called_at": lead.last_called_at.isoformat() if lead.last_called_at else None,
                "last_status": lead.last_status,
                "last_next_call_date": next_call.isoformat() if next_call else None,
            })

        return Response(result)
