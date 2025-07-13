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
    list_display = ('id', 'operator_display', 'lead_display', 'date', 'created')

    def operator_display(self, obj):
        return str(obj.operator) if obj.operator else "-"
    operator_display.short_description = "Operator"

    def lead_display(self, obj):
        return str(obj.lead) if obj.lead else "-"
    lead_display.short_description = "Lead"