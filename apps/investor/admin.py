from django.contrib import admin
from .models import InvestorMonthlyReport


# Register your models here.

from django.contrib import admin
from .models import InvestorMonthlyReport


@admin.register(InvestorMonthlyReport)
class InvestorMonthlyReportAdmin(admin.ModelAdmin):
    list_display = (
        'month', 'branch',
        'student_payment_sum_display',
        'student_extra_payment_sum_display',
        'student_payment_grand_total_display',
        'teacher_salaries_total_display',
        'user_salaries_total_display',
        'overhead_total_display',
        'capital_totals',
        'new_students_count',
        'attendance_total_debt',
        'attendance_remaining_debt',
        'attendance_discount_sum',
        'attendance_discount_pct',
    )

    list_filter = ('branch', 'month')
    search_fields = ('month', 'branch__name')

    # Custom display helpers
    def student_payment_sum_display(self, obj):
        return obj.student_payment_sum
    student_payment_sum_display.short_description = "Payment Sum"

    def student_extra_payment_sum_display(self, obj):
        return obj.student_extra_payment_sum
    student_extra_payment_sum_display.short_description = "Extra Payment"

    def student_payment_grand_total_display(self, obj):
        return obj.student_payment_grand_total
    student_payment_grand_total_display.short_description = "Grand Total"

    def teacher_salaries_total_display(self, obj):
        return obj.teacher_salaries_total
    teacher_salaries_total_display.short_description = "Teacher Salaries"

    def user_salaries_total_display(self, obj):
        return obj.user_salaries_total
    user_salaries_total_display.short_description = "User Salaries"

    def overhead_total_display(self, obj):
        return obj.overhead_total
    overhead_total_display.short_description = "Overheads"

    def capital_totals(self, obj):
        return f"{obj.capital_price_total} / {obj.capital_down_cost_total}"
    capital_totals.short_description = "Capital (Price/Down Cost)"

