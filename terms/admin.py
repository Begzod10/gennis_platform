from django.contrib import admin

from .models import Term, Test, Assignment


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'quarter', 'start_date', 'end_date','academic_year')
    search_fields = ('quarter','academic_year')
    list_filter = ('start_date', 'end_date','academic_year')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'weight', 'term', 'date', 'subject')
    search_fields = ('name',)
    list_filter = ('term', 'subject', 'date')
    autocomplete_fields = ('term', 'subject')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'percentage', 'test', 'date', 'student')
    search_fields = ('student__user__name', 'student__user__surname')
    list_filter = ('test', 'date')
    autocomplete_fields = ('test', 'student')
