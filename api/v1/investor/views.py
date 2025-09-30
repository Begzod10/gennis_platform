from rest_framework.views import APIView
from students.models import StudentPayment, Student
from overhead.models import Overhead
from capital.models import Capital
from teachers.models import TeacherSalaryList
from user.models import UserSalaryList
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Sum, F, IntegerField, ExpressionWrapper
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.investor.models import InvestorMonthlyReport


class InvestorView(APIView):
    """
    GET /api/investor-report?branch=3

    Reads precomputed monthly totals from InvestorMonthlyReport.
    Default month = current month (first day).
    """

    def _month_bounds(self, month_str: str):
        # month_str like "YYYY-MM" (we use current month below)
        if month_str:
            try:
                dt = datetime.strptime(month_str, "%Y-%m").date()
                start = dt.replace(day=1)
            except ValueError:
                return None, None
        else:
            start = timezone.localdate().replace(day=1)
        next_start = (start + timedelta(days=32)).replace(day=1)
        return start, next_start

    def get(self, request):
        # Current month only (as in your code). If you later want a ?month=YYYY-MM param, read it here.
        month_str = datetime.now().strftime("%Y-%m")
        start, nxt = self._month_bounds(month_str)
        if not start:
            return Response({"detail": "Invalid month format. Use YYYY-MM."},
                            status=status.HTTP_400_BAD_REQUEST)

        branch_id = request.query_params.get("branch")  # optional

        # Fetch snapshot row (global when branch is not provided)
        if branch_id:
            row = InvestorMonthlyReport.objects.filter(month=start, branch_id=branch_id).first()
        else:
            row = InvestorMonthlyReport.objects.filter(month=start, branch__isnull=True).first()

        snapshot_available = row is not None

        # If no snapshot yet, return zeros (frontend keeps same shape)
        if not snapshot_available:
            data = {
                "period": {"from": start.isoformat(), "to_lt": nxt.isoformat()},
                "filters": {"branch": branch_id},
                "snapshot_available": False,
                "student_payments": {
                    "total_payment_sum": 0,
                    "total_extra_payment": 0,
                    "grand_total": 0,
                },
                # Discount block is not stored in the model; return zeros to keep response stable.
                "student_per_month_discount": {
                    "total_discount": 0,
                    "total_extra_payment": 0,
                    "grand_total": 0,
                },
                "teacher_salaries": {"total_salary": 0},
                "user_salaries": {"total_user_salary": 0},
                "overheads": {"total_overhead": 0},
                "capital": {
                    "total_capital_price": 0,
                    "total_capital_down_cost": 0,
                },
                "new_students_count": 0,
            }
            return Response(data, status=status.HTTP_200_OK)

        # Map stored fields → your existing response shape
        data = {
            "period": {"from": start.isoformat(), "to_lt": nxt.isoformat()},
            "filters": {"branch": branch_id},
            "snapshot_available": True,

            "student_payments": {
                "total_payment_sum": row.student_payment_sum,
                "total_extra_payment": row.student_extra_payment_sum,
                "grand_total": row.student_payment_grand_total,
            },

            # Not tracked in the model; returning zeros to preserve API keys.
            "student_per_month_discount": {
                "total_discount": 0,
                "total_extra_payment": 0,
                "grand_total": 0,
            },

            "teacher_salaries": {"total_salary": row.teacher_salaries_total},
            "user_salaries": {"total_user_salary": row.user_salaries_total},
            "overheads": {"total_overhead": row.overhead_total},
            "capital": {
                "total_capital_price": row.capital_price_total,
                "total_capital_down_cost": row.capital_down_cost_total,
            },
            "new_students_count": row.new_students_count,
        }
        return Response(data, status=status.HTTP_200_OK)
