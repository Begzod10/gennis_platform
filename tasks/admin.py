from django.contrib import admin

from .models import Task, StudentCallInfo, TaskStatistics, TaskDailyStatistics, TaskStudent


# Register the Task model
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'auth_group', 'branch')
    search_fields = ('name', 'auth_group__name', 'branch__name')
    list_filter = ('auth_group', 'branch')


# Register the StudentCallInfo model
@admin.register(StudentCallInfo)
class StudentCallInfoAdmin(admin.ModelAdmin):
    list_display = ('student', 'task', 'created', 'delay_date', 'comment', 'user')
    search_fields = ('student__name', 'task__name', 'user__username', 'comment')
    list_filter = ('task', 'created', 'delay_date', 'user')


# Register the TaskStatistics model
@admin.register(TaskStatistics)
class TaskStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'completed_num', 'progress_num', 'percentage', 'day')
    search_fields = ('user__username', 'task__name', 'day')
    list_filter = ('task', 'day', 'user')


# Register the TaskDailyStatistics model
@admin.register(TaskDailyStatistics)
class TaskDailyStatisticsAdmin(admin.ModelAdmin):
    list_display = ('day', 'completed_num', 'progress_num', 'percentage', 'user')
    search_fields = ('day', 'user__username')
    list_filter = ('day', 'user')


# Register the TaskStudent model
@admin.register(TaskStudent)
class TaskStudentAdmin(admin.ModelAdmin):
    list_display = ('task', 'task_static', 'status', 'students')
    search_fields = ('task__name', 'task_static__user__username', 'students__name')
    list_filter = ('task', 'status')
