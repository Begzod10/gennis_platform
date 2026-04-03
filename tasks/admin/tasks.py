from django.utils.timezone import now
from django.db.models import Count, Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from attendances.models import AttendancePerMonth
from students.models import Student


class DebtorsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch')

        queryset = AttendancePerMonth.objects.filter(
            month_date__lte=today,
            status=False
        )

        if branch_id:
            queryset = queryset.filter(student__user__branch_id=branch_id)

        debts = (
            queryset
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
                total_debt=Sum('remaining_debt')
            )
        )

        result = []

        for item in debts:
            months = item['months_count']
            color = 'red' if months >= 2 else 'yellow'

            result.append({
                "full_name": f"{item['student__user__name']} {item['student__user__surname']}",
                "phone": item['student__user__phone'],
                "parent_phone": item['student__parents_number'],
                "debt": item['total_debt'] or 0,
                "months_count": months,
                "color": color
            })

        return Response(result)
