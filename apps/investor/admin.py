from django.contrib import admin
from .models import InvestorMonthlyReport


# Register your models here.


class InvestorMonthlyReportAdmin(admin.ModelAdmin):
    list_display = (
        'month',
        'branch',
        'payment_sum',
        'extra_payment',
        'grand_total',
        'teacher_salary',
        'user_salary',
        'overhead',
        'capital',
        'new_students',
    )

    list_filter = ('branch', 'month')

    search_fields = ('month', 'branch', 'branch__name')

    class Meta:
        model = InvestorMonthlyReport
