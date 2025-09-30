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


class InvestorView(APIView):
    """
    GET /api/investor-report?month=2025-09&branch=3

    Returns totals for the selected month (default: current month):
      - StudentPayment (by `date`): payment_sum, extra_payment, and grand_total
      - TeacherSalaryList (by `date`): total salaries
      - UserSalaryList (by `date`): total user salaries
      - Overhead (by `created`): total overhead
      - Capital (by `added_date`): price + total_down_cost
      - New students count (by `joined_group`)
    All queries ignore deleted=True and can be filtered by branch.
    """

    def _month_bounds(self, month_str: str):
        # month_str like "YYYY-MM"
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
        month_str = request.query_params.get("month")  # e.g. 2025-09
        branch_id = request.query_params.get("branch")  # e.g. 3
        month_str = "2025-09"
        branch_id = 8
        start, nxt = self._month_bounds(month_str)
        if not start:
            return Response(
                {"detail": "Invalid month format. Use YYYY-MM."},
                status=status.HTTP_400_BAD_REQUEST
            )

        branch_filter = {}
        if branch_id:
            branch_filter = {"branch_id": branch_id}

        # ---- StudentPayment (by date) ----
        sp_qs = StudentPayment.objects.filter(
            deleted=False, date__gte=start, date__lt=nxt, **branch_filter, status=False
        )
        sp_qs_discount = StudentPayment.objects.filter(
            deleted=False, date__gte=start, date__lt=nxt, **branch_filter, status=True
        )
        sp_total_expr = ExpressionWrapper(
            Coalesce(F("payment_sum"), 0) + Coalesce(F("extra_payment"), 0),
            output_field=IntegerField()
        )
        student_payments = sp_qs.aggregate(
            total_payment_sum=Coalesce(Sum("payment_sum"), 0),
            total_extra_payment=Coalesce(Sum("extra_payment"), 0),
            grand_total=Coalesce(Sum(sp_total_expr), 0),
        )
        student_discounts = sp_qs_discount.aggregate(
            total_discount=Coalesce(Sum("payment_sum"), 0),
            total_extra_payment=Coalesce(Sum("extra_payment"), 0),
            grand_total=Coalesce(Sum(sp_total_expr), 0),
        )
        # ---- TeacherSalaryList (by date) ----
        tsl_qs = TeacherSalaryList.objects.filter(
            deleted=False, date__gte=start, date__lt=nxt, **branch_filter
        )
        teacher_salaries = tsl_qs.aggregate(
            total_salary=Coalesce(Sum("salary"), 0)
        )

        # ---- UserSalaryList (by date) ----
        usl_qs = UserSalaryList.objects.filter(
            deleted=False, date__gte=start, date__lt=nxt, **branch_filter
        )
        user_salaries = usl_qs.aggregate(
            total_user_salary=Coalesce(Sum("salary"), 0)
        )

        # ---- Overhead (by created) ----
        oh_qs = Overhead.objects.filter(
            deleted=False, created__gte=start, created__lt=nxt, **branch_filter
        )
        overheads = oh_qs.aggregate(
            total_overhead=Coalesce(Sum("price"), 0)
        )

        # ---- Capital (by added_date) ----
        cap_qs = Capital.objects.filter(
            deleted=False, added_date__gte=start, added_date__lt=nxt, **branch_filter
        )
        capital = cap_qs.aggregate(
            total_capital_price=Coalesce(Sum("price"), 0),
            total_capital_down_cost=Coalesce(Sum("total_down_cost"), 0),
        )

        # ---- Students joined this month (by joined_group) ----
        new_students_count = Student.objects.filter(
            joined_group__gte=start, joined_group__lt=nxt
        ).count()

        data = {
            "period": {"from": start.isoformat(), "to_lt": nxt.isoformat()},
            "filters": {"branch": branch_id},
            "student_payments": student_payments,
            "student_per_month_discount": student_discounts,
            "teacher_salaries": teacher_salaries,
            "user_salaries": user_salaries,
            "overheads": overheads,
            "capital": capital,
            "new_students_count": new_students_count,
        }
        return Response(data, status=status.HTTP_200_OK)
