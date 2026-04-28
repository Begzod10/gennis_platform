from django.db import models
from django.db.models import Q
from branch.models import Branch


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
    overhead_gaz_total = models.BigIntegerField(default=0)
    overhead_svet_total = models.BigIntegerField(default=0)
    overhead_suv_total = models.BigIntegerField(default=0)
    overhead_arenda_total = models.BigIntegerField(default=0)
    overhead_oshxona_total = models.BigIntegerField(default=0)
    overhead_reklama_total = models.BigIntegerField(default=0)
    overhead_boshqa_total = models.BigIntegerField(default=0)

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


class ManagementDividend(models.Model):
    """Dividend paid out to the management project. Created/synced from gennis_management."""
    management_id = models.BigIntegerField(unique=True)
    amount = models.IntegerField()
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    payment_type = models.CharField(max_length=255, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='management_dividends')
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'dividend'
        managed = False

    def __str__(self):
        return f"Dividend {self.amount} – {self.date}"


class ManagementInvestment(models.Model):
    """Investment received from the management project. Created/synced from gennis_management."""
    management_id = models.BigIntegerField(unique=True)
    amount = models.IntegerField()
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    payment_type = models.CharField(max_length=255, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='management_investments')
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'management_investment'
        managed = False

    def __str__(self):
        return f"Investment {self.amount} – {self.date}"
