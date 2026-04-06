from django.utils.timezone import now
from datetime import timedelta
from django.db.models import OuterRef, Exists, Subquery
from django.db.models import Count, Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from attendances.models import AttendancePerMonth
from students.models import Student, CallLog
from user.models import CustomAutoGroup


class DebtorsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch_id')

        base_qs = AttendancePerMonth.objects.filter(
            month_date__lte=today,
            status=False
        )

        if branch_id:
            base_qs = base_qs.filter(student__user__branch_id=branch_id)

        # 🔥 Oxirgi call logni olish
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
                'student__parents_number'
            )
            .annotate(
                months_count=Count('id'),
                total_debt=Sum('remaining_debt'),

                last_next_call_date=Subquery(
                    last_call.values('next_call_date')[:1]
                )
            )
        )

        result = []

        for item in debts:
            next_call = item['last_next_call_date']

            # ❗ FILTER LOGIC
            if next_call and next_call > today:
                continue  # chiqarmaymiz

            months = item['months_count']
            color = 'red' if months >= 2 else 'yellow'

            result.append({
                "student_id": item['student'],
                "full_name": f"{item['student__user__name']} {item['student__user__surname']}",
                "phone": item['student__user__phone'],
                "parent_phone": item['student__parents_number'],
                "debt": item['total_debt'] or 0,
                "months_count": months,
                "color": color
            })

        return Response(result)


class CreateCallLogAPIView(APIView):
    def post(self, request):
        category = request.data.get('category')
        status = request.data.get('status')

        today = now().date()

        comment = request.data.get('comment')
        next_call_date = request.data.get('next_call_date')

        student_id = request.data.get('student_id')
        lead_id = request.data.get('lead_id')

        # 🔥 AUTO LOGIC
        if status == 'not_answered':
            comment = "tel ko'tarmadi"
            next_call_date = today + timedelta(days=1)

        obj = CallLog.objects.create(
            category=category,
            student_id=student_id if category != 'lead' else None,
            lead_id=lead_id if category == 'lead' else None,
            status=status,
            comment=comment,
            next_call_date=next_call_date,
            audio=request.FILES.get('audio')
        )

        return Response({"message": "Saved"})
