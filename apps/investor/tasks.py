from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, F, IntegerField, ExpressionWrapper
from django.db.models.functions import Coalesce
from celery import shared_task
from django.apps import apps as django_apps


def _month_bounds():
    start = timezone.localdate().replace(day=1)
    nxt = (start + timedelta(days=32)).replace(day=1)
    return start, nxt


def _compute_totals(start, nxt, branch_id=None):
    # Lazy get models to avoid import cycles; adjust app labels if needed.
    StudentPayment = django_apps.get_model('students', 'StudentPayment')
    TeacherSalaryList = django_apps.get_model('teachers', 'TeacherSalaryList')
    UserSalaryList = django_apps.get_model('user', 'UserSalaryList')  # <- if different, change app label
    Overhead = django_apps.get_model('overhead', 'Overhead')
    Capital = django_apps.get_model('capital', 'Capital')
    Student = django_apps.get_model('students', 'Student')

    branch_filter = {"branch_id": branch_id} if branch_id else {}

    # StudentPayment: only income (status=False) exactly like your view
    sp_qs = StudentPayment.objects.filter(
        deleted=False, date__gte=start, date__lt=nxt, status=False, **branch_filter
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

    teacher_salaries = TeacherSalaryList.objects.filter(
        deleted=False, date__gte=start, date__lt=nxt, **branch_filter
    ).aggregate(total_salary=Coalesce(Sum("salary"), 0))

    user_salaries = UserSalaryList.objects.filter(
        deleted=False, date__gte=start, date__lt=nxt, **branch_filter
    ).aggregate(total_user_salary=Coalesce(Sum("salary"), 0))

    overheads = django_apps.get_model('overhead', 'Overhead').objects.filter(
        deleted=False, created__gte=start, created__lt=nxt, **branch_filter
    ).aggregate(total_overhead=Coalesce(Sum("price"), 0))

    capital = django_apps.get_model('capital', 'Capital').objects.filter(
        deleted=False, added_date__gte=start, added_date__lt=nxt, **branch_filter
    ).aggregate(
        total_capital_price=Coalesce(Sum("price"), 0),
        total_capital_down_cost=Coalesce(Sum("total_down_cost"), 0),
    )

    new_students_count = Student.objects.filter(
        joined_group__gte=start, joined_group__lt=nxt
    ).count()

    return {
        "student_payment_sum": int(student_payments["total_payment_sum"]),
        "student_extra_payment_sum": int(student_payments["total_extra_payment"]),
        "student_payment_grand_total": int(student_payments["grand_total"]),
        "teacher_salaries_total": int(teacher_salaries["total_salary"] or 0),
        "user_salaries_total": int(user_salaries["total_user_salary"] or 0),
        "overhead_total": int(overheads["total_overhead"] or 0),
        "capital_price_total": int(capital["total_capital_price"] or 0),
        "capital_down_cost_total": int(capital["total_capital_down_cost"] or 0),
        "new_students_count": int(new_students_count),
    }


@shared_task(name="apps.investor.tasks.snapshot_investor_month")
def snapshot_investor_month():
    """
    Compute & save current-month snapshot for:
      - Global (branch=None)
      - Each branch
    Safe to run daily; uses update_or_create.
    """
    InvestorMonthlyReport = django_apps.get_model('investor', 'InvestorMonthlyReport')
    Branch = django_apps.get_model('branch', 'Branch')

    start, nxt = _month_bounds()

    with transaction.atomic():
        # Global (all branches)
        totals_global = _compute_totals(start, nxt, branch_id=None)
        InvestorMonthlyReport.objects.update_or_create(
            month=start, branch=None, defaults=totals_global
        )

        # Per-branch
        for b in Branch.objects.all().only("id"):
            totals = _compute_totals(start, nxt, branch_id=b.id)
            InvestorMonthlyReport.objects.update_or_create(
                month=start, branch_id=b.id, defaults=totals
            )
    return "OK"
