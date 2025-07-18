from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

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

    def changelist_view(self, request, extra_context=None):
        branch_lead_counts = (
            Lead.objects.values('branch__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        # HTML ko'rinishini tayyorlash
        branch_summary = "<ul>"
        for branch in branch_lead_counts:
            branch_summary += f"<li><strong>{branch['branch__name']}</strong>: {branch['total']} ta lead</li>"
        branch_summary += "</ul>"

        extra_context = extra_context or {}
        extra_context['title'] = "Leads by Branch"
        extra_context['branch_summary'] = format_html(branch_summary)

        return super().changelist_view(request, extra_context=extra_context)

    def get_changelist(self, request, **kwargs):
        from django.contrib.admin.views.main import ChangeList

        class CustomChangeList(ChangeList):
            def get_results(self, *args, **kwargs):
                super().get_results(*args, **kwargs)
                if hasattr(self.model_admin, 'extra_context'):
                    self.model_admin.extra_context.update(self.model_admin.extra_context)

        return CustomChangeList


@admin.register(LeadCall)
class LeadCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'status', 'created', 'delay', 'deleted', 'is_agreed')
    list_filter = ('lead', 'status', 'deleted', 'is_agreed','lead__branch')
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
