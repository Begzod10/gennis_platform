from django.contrib import admin

from .models import Subject, SubjectLevel


# Register the Subject model
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'ball_number', 'old_id')
    search_fields = ('name',)
    # list_filter = ('disabled',)
    ordering = ('name',)


# Register the SubjectLevel model
@admin.register(SubjectLevel)
class SubjectLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'old_id')
    search_fields = ('name', 'subject__name')
    # list_filter = ('disabled', 'subject')
    ordering = ('name',)
