from django.utils.timezone import now
from datetime import timedelta
from django.db.models import OuterRef, Exists, Subquery
from django.db.models import Count, Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from attendances.models import AttendancePerMonth
from students.models import Student, CallLog, DeletedStudent
from user.models import CustomAutoGroup


class DebtorsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch')

        base_qs = AttendancePerMonth.objects.filter(
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
            )
            .annotate(
                months_count=Count('id'),
                total_debt=Sum('remaining_debt'),
                last_next_call_date=Subquery(last_call.values('next_call_date')[:1]),
            )
        )
        print(debts.count())

        result = []
        for item in debts:
            next_call = item['last_next_call_date']
            if next_call and next_call > today:
                continue  # hali vaqti kelmagan, ko'rsatmaymiz

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
            })

        return Response(result)
