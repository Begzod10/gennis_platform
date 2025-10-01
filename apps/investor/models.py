from django.db import models
from django.db.models import Q


class InvestorMonthlyReport(models.Model):
    """
    One row per month (+ optional branch).
    Save sums you computed in the InvestorView into these fields.
    """
    month = models.DateField(help_text="Use the first day of the month, e.g. 2025-09-01")
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='investor_reports'
    )

    attendance_total_debt = models.BigIntegerField(default=0)
    attendance_remaining_debt = models.BigIntegerField(default=0)
    attendance_discount_sum = models.BigIntegerField(default=0)
    attendance_discount_pct = models.IntegerField(default=0)  # 0..10
    total_students = models.IntegerField(default=0)

    # ---- Totals (integers like your source models) ----
    student_payment_sum = models.BigIntegerField(default=0)  # Sum of StudentPayment.payment_sum
    student_extra_payment_sum = models.BigIntegerField(default=0)  # Sum of StudentPayment.extra_payment
    student_payment_grand_total = models.BigIntegerField(default=0)  # payment_sum + extra_payment

    teacher_salaries_total = models.BigIntegerField(default=0)  # Sum of TeacherSalaryList.salary
    user_salaries_total = models.BigIntegerField(default=0)  # Sum of UserSalaryList.salary

    overhead_total = models.BigIntegerField(default=0)  # Sum of Overhead.price

    capital_price_total = models.BigIntegerField(default=0)  # Sum of Capital.price
    capital_down_cost_total = models.BigIntegerField(default=0)  # Sum of Capital.total_down_cost

    new_students_count = models.IntegerField(default=0)  # Count of Student joined in month

    # ---- Metadata ----
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['month']),
            models.Index(fields=['branch']),
            models.Index(fields=['month', 'branch']),
        ]
        constraints = [
            # Ensure only one row per (month, branch)
            models.UniqueConstraint(
                fields=['month', 'branch'],
                name='uniq_investor_report_month_branch'
            ),
            # Ensure only one GLOBAL row per month (when branch is NULL)
            models.UniqueConstraint(
                fields=['month'],
                condition=Q(branch__isnull=True),
                name='uniq_investor_report_month_global'
            ),
        ]

    def __str__(self):
        scope = self.branch.name if self.branch_id else "All branches"
        return f"Investor report {self.month:%Y-%m} – {scope}"
