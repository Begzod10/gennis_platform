from django.contrib import admin

from .models import (
    TeacherSalaryType, Teacher, TeacherAttendance,
    TeacherSalary, TeacherBlackSalary, TeacherSalaryList,
    TeacherGroupStatistics, TeacherHistoryGroups
)


# Register the TeacherSalaryType model
@admin.register(TeacherSalaryType)
class TeacherSalaryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary')
    search_fields = ('name',)
    ordering = ('name',)


# Register the Teacher model
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'color', 'total_students', 'premium_rate', 'class_type', 'teacher_salary_type', 'old_id')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('teacher_salary_type', 'branches')
    filter_horizontal = ('subject', 'branches', 'group_time_table')


# Register the TeacherAttendance model
@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'day', 'status', 'system')
    search_fields = ('teacher__user__username', 'system__name')
    list_filter = ('status', 'system')


# Register the TeacherSalary model
@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = (
    'teacher', 'month_date', 'total_salary', 'remaining_salary', 'taken_salary', 'total_black_salary', 'percentage',
    'branch')
    search_fields = ('teacher__user__username', 'branch__name')
    list_filter = ('month_date', 'branch', 'teacher_salary_type')
    date_hierarchy = 'month_date'


# Register the TeacherBlackSalary model
@admin.register(TeacherBlackSalary)
class TeacherBlackSalaryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'black_salary', 'group', 'student', 'month_date', 'status')
    search_fields = ('teacher__user__username', 'student__user__username')
    list_filter = ('group', 'status')


# Register the TeacherSalaryList model
@admin.register(TeacherSalaryList)
class TeacherSalaryListAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'salary_id', 'payment', 'date', 'comment', 'branch', 'deleted', 'salary')
    search_fields = ('teacher__user__username', 'salary_id__teacher__user__username', 'payment__name', 'branch__name')
    list_filter = ('date', 'branch', 'deleted')


# Register the TeacherGroupStatistics model
@admin.register(TeacherGroupStatistics)
class TeacherGroupStatisticsAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'reason', 'branch', 'number_students', 'percentage', 'date')
    search_fields = ('teacher__user__username', 'reason__name', 'branch__name')
    list_filter = ('branch', 'date')


# Register the TeacherHistoryGroups model
@admin.register(TeacherHistoryGroups)
class TeacherHistoryGroupsAdmin(admin.ModelAdmin):
    list_display = ('group', 'teacher', 'reason', 'joined_day', 'left_day')
    search_fields = ('group__name', 'teacher__user__username', 'reason')
    list_filter = ('group', 'joined_day', 'left_day')
    date_hierarchy = 'joined_day'
