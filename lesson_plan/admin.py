from django.contrib import admin

from .models import LessonPlan, LessonPlanStudents


# Register the LessonPlan model
@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ('group', 'teacher', 'date', 'updated')
    search_fields = ('group__name', 'teacher__user__username', 'objective')
    list_filter = ('group', 'teacher', 'date', 'updated')
    ordering = ('-date',)


# Register the LessonPlanStudents model
@admin.register(LessonPlanStudents)
class LessonPlanStudentsAdmin(admin.ModelAdmin):
    list_display = ('lesson_plan', 'student', 'comment')
    search_fields = ('lesson_plan__group__name', 'student__user__username', 'comment')
    list_filter = ('lesson_plan__date', 'student')
    ordering = ('lesson_plan',)
