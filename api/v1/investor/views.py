
from datetime import timedelta, datetime
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.investor.models import InvestorMonthlyReport
from user.models import CustomUser, CustomAutoGroup
from rest_framework.permissions import IsAuthenticated



class BranchInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        branch = getattr(user, "branch", None)

        if branch is None:
            return Response({"detail": "User has no branch assigned."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the row that belongs to THIS user.
        # If you want to ensure it also matches the same branch: add .filter(user__branch=branch)
        row = (CustomAutoGroup.objects
               .select_related("group")
               .filter(user=user)  # <-- was .filter(branch=branch, user=user) (invalid)
               .values("group_id", "group__name", "share")
               .first())

        info = {
            "branch": [{"id": branch.id, "name": branch.name, "share": row["share"] if row else None}],
            "group": {"id": row["group_id"], "name": row["group__name"]} if row else None,

        }
        return Response(info, status=status.HTTP_200_OK)


class InvestorView(APIView):
    permission_classes = [IsAuthenticated]
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



class InvestorReportView(APIView):
    permission_classes = [IsAuthenticated]
    """
    GET /api/investor-report?branch=3

    Reads precomputed monthly totals from InvestorMonthlyReport (current month).
    """

    def get(self, request):
        type_data = request.query_params.get("type")
        branch_id = request.query_params.get("branch")  # optional

        # Fetch snapshot row (global when branch is not provided)
        if branch_id:
            row = InvestorMonthlyReport.objects.filter(branch_id=branch_id).order_by("-month").all()
        else:
            row = InvestorMonthlyReport.objects.filter(branch__isnull=True).order_by("-month").all()
        print(branch_id)
        print(type_data)
        if type_data == "payments":
            data = {
                "period": {"from": row.first().month, "to": row.last().month},
                "filters": {"branch": branch_id},
                "payments": {
                    "due_this_month": row.last().attendance_total_debt,
                    "due_this_day": row.last().student_payment_sum,
                    "outstanding": row.last().attendance_remaining_debt,
                }}
            return Response(data, status=status.HTTP_200_OK)
        elif type_data == "expenses":
            data = {
                "period": {"from": row.first().month, "to": row.last().month},
                "filters": {"branch": branch_id},
                "expenses": {
                    "salaries": row.last().teacher_salaries_total + row.last().user_salaries_total,
                    "additional": row.last().overhead_total - row.last().overhead_oshxona_total,
                    "cafeteria": row.last().overhead_oshxona_total,
                    "capital": row.last().capital_price_total,
                }}
            return Response(data, status=status.HTTP_200_OK)
        elif type_data == "students":
            data = {
                "period": {"from": row.first().month, "to": row.last().month},
                "filters": {"branch": branch_id},
                "students": row.last().total_students,
                "new_students": row.last().new_students_count,
            }
            return Response(data, status=status.HTTP_200_OK)

