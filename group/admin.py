from django.contrib import admin

from .models import (
    CourseTypes, Group, GroupReason,
    AttendancePerMonth, AttendancePerDay
)


# Register the CourseTypes model
@admin.register(CourseTypes)
class CourseTypesAdmin(admin.ModelAdmin):
    list_display = ('name', 'old_id')
    search_fields = ('name',)
    ordering = ('name',)


# Register the Group model
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'subject', 'level', 'branch', 'status', 'created_date', 'language', 'system', 'course_types')
    search_fields = ('name', 'subject__name', 'teacher__user__username', 'branch__name')
    list_filter = ('subject', 'branch', 'status', 'created_date', 'language', 'system', 'course_types')
    filter_horizontal = ('students', 'teacher')
    ordering = ('-created_date',)


# Register the GroupReason model
@admin.register(GroupReason)
class GroupReasonAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


# Register the AttendancePerMonth model
@admin.register(AttendancePerMonth)
class AttendancePerMonthAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'student', 'group', 'month_date', 'status', 'total_debt', 'total_salary', 'payment')
    search_fields = ('teacher__user__username', 'student__user__username', 'group__name')
    list_filter = ('month_date', 'group', 'teacher', 'status')
    ordering = ('-month_date',)


# Register the AttendancePerDay model
@admin.register(AttendancePerDay)
class AttendancePerDayAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'group', 'day', 'average', 'status')
    search_fields = ('student__user__username', 'teacher__user__username', 'group__name')
    list_filter = ('day', 'group', 'teacher', 'status')
    ordering = ('-day',)
