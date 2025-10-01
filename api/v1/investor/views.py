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
from user.models import CustomUser, CustomAutoGroup


class BranchInfoView(APIView):
    def get(self, request):
        branch = request.user.branch
        group_get = CustomAutoGroup.objects.get(user=branch)
        info = {
            "branch": [
                {
                    "id": branch.id,
                    "name": branch.name
                }
            ],

            "group": group_get.group,
            "share": group_get.share
        }

        return Response(info, status=status.HTTP_200_OK)


class InvestorView(APIView):
    """
    GET /api/investor-report?branch=3

    Reads precomputed monthly totals from InvestorMonthlyReport (current month).
    """

    def _month_bounds(self, month_str: str):
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
        month_str = datetime.now().strftime("%Y-%m")  # current month
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
        branch_id = 8

        def zero_payload():
            return {
                "period": {"from": start.isoformat(), "to_lt": nxt.isoformat()},
                "filters": {"branch": branch_id},
                "snapshot_available": False,
                "student_payments": {
                    "total_payment_sum": 0,
                    "total_extra_payment": 0,
                    "grand_total": 0,
                },
                # Not tracked in the model (unless you add fields for it):
                "student_per_month_discount": {
                    "total_discount": 0,
                    "total_extra_payment": 0,
                    "grand_total": 0,
                    "total_debt": 0,
                    "remaining_debt": 0,
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

        if not snapshot_available:
            return Response(zero_payload(), status=status.HTTP_200_OK)

        data = {
            "period": {"from": start.isoformat(), "to_lt": nxt.isoformat()},
            "filters": {"branch": branch_id},
            "snapshot_available": True,

            "payments": {
                "due_this_month": getattr(row, "attendance_total_debt", 0),
                "due_this_day": row.student_payment_sum,
                "outstanding": getattr(row, "attendance_remaining_debt", 0),
            },
            "expenses": {
                "salaries": row.teacher_salaries_total + row.user_salaries_total,
                "additional": row.overhead_total - row.overhead_oshxona_total,
                "cafeteria": row.overhead_oshxona_total,
                "capital": row.capital_price_total,
            },
            "students": row.total_students,
            "new_students": row.new_students_count,
        }
        return Response(data, status=status.HTTP_200_OK)
