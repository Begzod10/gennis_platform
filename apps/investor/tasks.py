from django.db import transaction
from django.db.models import Sum, F, IntegerField, ExpressionWrapper
from django.db.models.functions import Coalesce
from celery import shared_task
from django.apps import apps as django_apps
from branch.models import Location
from system.models import System
from students.models import DeletedStudent, DeletedNewStudent
from group.models import Group
from django.db.models import Prefetch
from datetime import date, timedelta
from typing import Optional, Tuple
from django.utils import timezone


def month_bounds(
        target: Optional[date] = None,
        months_ago: int = 1,
        inclusive_end: bool = True,
) -> Tuple[date, date]:
    if target is None:
        target = timezone.localdate()

    first_of_month = target.replace(day=1)

    y = first_of_month.year
    m = first_of_month.month - months_ago
    while m <= 0:
        y -= 1
        m += 12

    month_start = date(y, m, 1)
    next_month_start = (month_start + timedelta(days=32)).replace(day=1)

    if inclusive_end:
        return month_start, next_month_start - timedelta(days=1)
    return month_start, next_month_start


def _compute_totals(start, nxt, branch_id=None):
    StudentPayment = django_apps.get_model('students', 'StudentPayment')
    TeacherSalaryList = django_apps.get_model('teachers', 'TeacherSalaryList')
    UserSalaryList = django_apps.get_model('user', 'UserSalaryList')  # adjust if different
    Overhead = django_apps.get_model('overhead', 'Overhead')
    OverheadType = django_apps.get_model('overhead', 'OverheadType')
    Capital = django_apps.get_model('capital', 'Capital')
    Student = django_apps.get_model('students', 'Student')
    AttendancePerMonth = django_apps.get_model('attendances', 'AttendancePerMonth')

    branch_filter = {"branch_id": branch_id} if branch_id else {}

    # ---- StudentPayment (income)
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

    # ---- Overhead (overall)
    overhead_qs = Overhead.objects.filter(
        deleted=False, created__gte=start, created__lt=nxt, **branch_filter
    )
    overheads = overhead_qs.aggregate(total_overhead=Coalesce(Sum("price"), 0))

    # ---- NEW: Overhead per type (IDs from your table)
    TYPE_IDS = {
        "gaz": 5,
        "svet": 6,
        "suv": 7,
        "arenda": 8,
        "oshxona": 12,
        "reklama": 13,
        "boshqa": 9,
    }
    rows = (
        overhead_qs
        .values("type_id")
        .annotate(total=Coalesce(Sum("price"), 0))
    )
    by_id = {r["type_id"]: int(r["total"] or 0) for r in rows}

    gaz_total = by_id.get(TYPE_IDS["gaz"], 0)
    svet_total = by_id.get(TYPE_IDS["svet"], 0)
    suv_total = by_id.get(TYPE_IDS["suv"], 0)
    arenda_total = by_id.get(TYPE_IDS["arenda"], 0)
    oshxona_total = by_id.get(TYPE_IDS["oshxona"], 0)
    reklama_total = by_id.get(TYPE_IDS["reklama"], 0)
    boshqa_total = by_id.get(TYPE_IDS["boshqa"], 0)

    capital = Capital.objects.filter(
        deleted=False, added_date__gte=start, added_date__lt=nxt, **branch_filter
    ).aggregate(
        total_capital_price=Coalesce(Sum("price"), 0),
        total_capital_down_cost=Coalesce(Sum("total_down_cost"), 0),
    )

    new_students_count = Student.objects.filter(
        joined_group__gte=start, joined_group__lt=nxt
    ).count()
    deleted_student_ids = DeletedStudent.objects.filter(
        student__groups_student__isnull=True,
        deleted=False
    ).values_list('student_id', flat=True)

    deleted_new_student_ids = DeletedNewStudent.objects.values_list(
        'student_id', flat=True
    )

    active_students = Student.objects.select_related(
        'user',
        'user__language',
        'class_number'
    ).prefetch_related(
        'user__student_user',
        Prefetch(
            'groups_student',
            queryset=Group.objects.select_related('class_number', 'color').order_by('id'),
            to_attr='prefetched_groups'
        )
    ).exclude(
        id__in=deleted_student_ids
    ).exclude(
        id__in=deleted_new_student_ids
    ).filter(
        groups_student__isnull=False,
    )
    if branch_id:
        active_students = active_students.filter(user__branch_id=branch_id)
    active_students = active_students.distinct().order_by('class_number__number').count()

    # ---- AttendancePerMonth (by month_date; branch via Group)
    att_branch_filter = {}
    if branch_id is not None:
        att_branch_filter = {"group__branch_id": branch_id}

    att_qs = AttendancePerMonth.objects.filter(
        month_date__gte=start, month_date__lt=nxt,
        **att_branch_filter
    )

    att_aggr = att_qs.aggregate(
        total_debt=Coalesce(Sum("total_debt"), 0),
        remaining_debt=Coalesce(Sum("remaining_debt"), 0),
        discount_sum=Coalesce(Sum("discount"), 0),
    )

    total_debt = int(att_aggr["total_debt"] or 0)
    discount_sum = int(att_aggr["discount_sum"] or 0)
    remaining_debt = int(att_aggr["remaining_debt"] or 0)
    discount_pct = int(round((discount_sum / total_debt) * 100)) if total_debt else 0

    return {
        "student_payment_sum": int(student_payments["total_payment_sum"] or 0),
        "student_extra_payment_sum": int(student_payments["total_extra_payment"] or 0),
        "student_payment_grand_total": int(student_payments["grand_total"] or 0),

        "teacher_salaries_total": int(teacher_salaries["total_salary"] or 0),
        "user_salaries_total": int(user_salaries["total_user_salary"] or 0),

        "overhead_total": int(overheads["total_overhead"] or 0),

        # NEW per-type overhead totals
        "overhead_gaz_total": gaz_total,
        "overhead_svet_total": svet_total,
        "overhead_suv_total": suv_total,
        "overhead_arenda_total": arenda_total,
        "overhead_oshxona_total": oshxona_total,
        "overhead_reklama_total": reklama_total,
        "overhead_boshqa_total": boshqa_total,

        "capital_price_total": int(capital["total_capital_price"] or 0),
        "capital_down_cost_total": int(capital["total_capital_down_cost"] or 0),

        "new_students_count": int(new_students_count or 0),
        "total_students": int(active_students or 0),

        # Attendance totals
        "attendance_total_debt": total_debt,
        "attendance_remaining_debt": remaining_debt,
        "attendance_discount_sum": discount_sum,
        "attendance_discount_pct": discount_pct,
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

    start, end = month_bounds(months_ago=0, inclusive_end=True)
    get_system = System.objects.filter(name="school").first()
    get_location = Location.objects.filter(system=get_system).all()
    with transaction.atomic():
        # Global (all branches)
        totals_global = _compute_totals(start, end, branch_id=None)
        InvestorMonthlyReport.objects.update_or_create(
            month=start, branch=None, defaults=totals_global
        )

        # Per-branch
        for b in Branch.objects.filter(location__in=get_location).all().only("id"):
            totals = _compute_totals(start, end, branch_id=b.id)
            InvestorMonthlyReport.objects.update_or_create(
                month=start, branch_id=b.id, defaults=totals
            )
    return "OK"
