from django.contrib import admin

from .models import LeadBlock, Lead, LeadCall, OperatorPercent, OperatorLead


@admin.register(LeadBlock)
class LeadBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'branch', 'deleted')
    list_filter = ('branch', 'deleted')
    search_fields = ('name',)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'branch', 'created', 'finished', 'deleted')
    list_filter = ('branch', 'finished', 'deleted')
    search_fields = ('name', 'phone', 'surname')


@admin.register(LeadCall)
class LeadCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'status', 'created', 'delay', 'deleted', 'is_agreed')
    list_filter = ('status', 'deleted', 'is_agreed')
    search_fields = ('comment',)


@admin.register(OperatorPercent)
class OperatorPercentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'percent', 'total_lead', 'accepted', 'date')
    list_filter = ('date',)
    search_fields = ('user__username',)


@admin.register(OperatorLead)
class OperatorLeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'operator', 'lead', 'date', 'created')
    list_filter = ('date', 'operator')
    search_fields = ('lead__name', 'operator__username')
