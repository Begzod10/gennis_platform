from django.contrib import admin

from .models import AttendancePerMonth, AttendancePerDay, GroupAttendancesPerMonth


# Register the AttendancePerMonth model
@admin.register(AttendancePerMonth)
class AttendancePerMonthAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'teacher', 'group', 'status', 'total_debt',
        'total_salary', 'ball_percentage', 'month_date', 'total_charity',
        'remaining_debt', 'payment', 'remaining_salary', 'taken_salary',
        'present_days', 'absent_days', 'scored_days', 'old_id'
    )
    search_fields = (
        'student__user__username', 'teacher__user__username', 'group__name',
        'month_date', 'old_id'
    )
    list_filter = ('group', 'teacher', 'month_date', 'status')
    ordering = ('-month_date',)


# Register the AttendancePerDay model
@admin.register(AttendancePerDay)
class AttendancePerDayAdmin(admin.ModelAdmin):
    list_display = (
        'attendance_per_month', 'debt_per_day', 'salary_per_day', 'student',
        'teacher', 'charity_per_day', 'group', 'day', 'homework_ball',
        'dictionary_ball', 'activeness_ball', 'average', 'status', 'old_id',
        'reason', 'teacher_ball'
    )
    search_fields = (
        'student__user__username', 'teacher__user__username', 'group__name',
        'day', 'old_id'
    )
    list_filter = ('group', 'teacher', 'day', 'status')
    ordering = ('-day',)


# Register the GroupAttendancesPerMonth model
@admin.register(GroupAttendancesPerMonth)
class GroupAttendancesPerMonthAdmin(admin.ModelAdmin):
    list_display = (
        'group', 'total_debt', 'total_salary', 'month_date',
        'total_charity', 'remaining_debt', 'payment',
        'remaining_salary', 'taken_salary'
    )
    search_fields = ('group__name', 'month_date')
    list_filter = ('group', 'month_date')
    ordering = ('-month_date',)
