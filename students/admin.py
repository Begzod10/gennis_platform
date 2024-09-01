from django.contrib import admin

from .models import (
    Student, StudentCharity, StudentPayment,
    DeletedNewStudent, StudentHistoryGroups,
    DeletedStudent, ContractStudent
)


# Register the Student model
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_payment_month', 'debt_status', 'shift', 'parents_number', 'representative_name',
                    'representative_surname', 'old_id')
    search_fields = ('user__username', 'representative_name', 'representative_surname', 'parents_number')
    list_filter = ('shift', 'debt_status')
    filter_horizontal = ('subject', 'group_time_table')


# Register the StudentCharity model
@admin.register(StudentCharity)
class StudentCharityAdmin(admin.ModelAdmin):
    list_display = ('student', 'charity_sum', 'group', 'branch', 'added_data')
    search_fields = ('student__user__username', 'group__name', 'branch__name')
    list_filter = ('group', 'branch', 'added_data')


# Register the StudentPayment model
@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'payment_type', 'payment_sum', 'branch', 'added_data', 'status', 'deleted', 'old_id')
    search_fields = ('student__user__username', 'payment_type__name', 'branch__name')
    list_filter = ('status', 'deleted', 'branch', 'payment_type')
    date_hierarchy = 'added_data'


# Register the DeletedNewStudent model
@admin.register(DeletedNewStudent)
class DeletedNewStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'created', 'comment')
    search_fields = ('student__user__username', 'comment')
    list_filter = ('created',)


# Register the StudentHistoryGroups model
@admin.register(StudentHistoryGroups)
class StudentHistoryGroupsAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'teacher', 'reason', 'joined_day', 'left_day', 'old_id')
    search_fields = ('student__user__username', 'group__name', 'teacher__user__username')
    list_filter = ('group', 'teacher', 'joined_day', 'left_day')
    date_hierarchy = 'joined_day'


# Register the DeletedStudent model
@admin.register(DeletedStudent)
class DeletedStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'teacher', 'group_reason', 'deleted_date', 'old_id')
    search_fields = ('student__user__username', 'group__name', 'teacher__user__username', 'group_reason__name')
    list_filter = ('group', 'teacher', 'deleted_date')
    date_hierarchy = 'deleted_date'


# Register the ContractStudent model
@admin.register(ContractStudent)
class ContractStudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_date', 'expire_date', 'father_name', 'place', 'passport_series', 'old_id')
    search_fields = ('student__user__username', 'father_name', 'passport_series', 'place')
    list_filter = ('created_date', 'expire_date')
    date_hierarchy = 'created_date'
