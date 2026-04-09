from django.contrib import admin

from group.models import Group
from students.models import Student
from .models import (
    Party, PartyMember, PartyTask, PartyTaskGrade,
    Competition, CompetitionResult,
)


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ball', 'rating', 'color']
    search_fields = ['name']
    filter_horizontal = ['students', 'groups']







@admin.register(PartyMember)
class PartyMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'party', 'student', 'role', 'ball', 'status', 'is_active']
    list_filter = ['party', 'role', 'status']


@admin.register(PartyTask)
class PartyTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ball', 'deadline', 'is_completed']
    filter_horizontal = ['parties']


@admin.register(PartyTaskGrade)
class PartyTaskGradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'party', 'ball', 'graded_at']


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'emoji', 'color']


@admin.register(CompetitionResult)
class CompetitionResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'competition', 'party', 'quarter', 'ball', 'is_winner']
    list_filter = ['quarter', 'is_winner']
