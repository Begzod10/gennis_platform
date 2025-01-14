from django.contrib import admin

from .models import Hours, ClassTimeTable


# Register the Hours model
@admin.register(Hours)
class HoursAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'order')
    search_fields = ('name',)
    ordering = ('order',)


# Register the ClassTimeTable model
@admin.register(ClassTimeTable)
class ClassTimeTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'date', 'room', 'hours', 'branch', 'teacher', 'subject', 'flow')
    search_fields = ('name', 'group__name', 'room__name', 'teacher__user__username', 'subject__name')
    list_filter = ('week', 'branch', 'teacher', 'subject')
    filter_horizontal = ('students',)
