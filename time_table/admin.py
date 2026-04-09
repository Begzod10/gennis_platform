from django.contrib import admin

from .models import WeekDays, GroupTimeTable, TimeTableArchive, StudentTimTableArchive


# Register the WeekDays model
@admin.register(WeekDays)
class WeekDaysAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_uz', 'order')
    search_fields = ('name_en', 'name_uz')
    ordering = ('order',)


# Register the GroupTimeTable model
@admin.register(GroupTimeTable)
class GroupTimeTableAdmin(admin.ModelAdmin):
    list_display = ('group', 'week', 'room', 'start_time', 'end_time', 'branch', 'old_id')
    search_fields = ('group__name', 'week__name_en', 'week__name_uz', 'room__name', 'branch__name')
    list_filter = ('group', 'week', 'room', 'branch')


# Register the TimeTableArchive model
@admin.register(TimeTableArchive)
class TimeTableArchiveAdmin(admin.ModelAdmin):
    list_display = ('group', 'week', 'room', 'start_time', 'end_time', 'date')
    search_fields = ('group__name', 'week__name_en', 'week__name_uz', 'room__name')
    list_filter = ('group', 'week', 'room', 'date')
    date_hierarchy = 'date'


# Register the StudentTimTableArchive model
@admin.register(StudentTimTableArchive)
class StudentTimTableArchiveAdmin(admin.ModelAdmin):
    list_display = ('student', 'archive')
    search_fields = ('student__name', 'archive__group__name')
    list_filter = ('student', 'archive__group')
