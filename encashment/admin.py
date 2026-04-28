from django.contrib import admin

from .models import Encashment


# Register the Encashment model
@admin.register(Encashment)
class EncashmentAdmin(admin.ModelAdmin):
    list_display = (
        'ot', 'do', 'payment_type', 'branch',
        'total_teacher_salary', 'total_student_payment',
        'total_staff_salary', 'total_branch_payment',
        'total_overhead', 'total_capital'
    )
    search_fields = (
        'payment_type__name', 'branch__name'
    )
    list_filter = (
        'ot', 'do', 'payment_type', 'branch'
    )
    ordering = ('-ot',)
