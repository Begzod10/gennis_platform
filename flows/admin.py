from django.contrib import admin

from .models import FlowTypes, Flow


# Register the FlowTypes model
@admin.register(FlowTypes)
class FlowTypesAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name', 'color')
    ordering = ('name',)


# Register the Flow model
@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ('name', 'flow_type', 'subject', 'teacher', 'activity', 'level')
    search_fields = ('name', 'flow_type__name', 'subject__name', 'teacher__user__username', 'level__name')
    list_filter = ('flow_type', 'subject', 'teacher', 'activity', 'level')
    filter_horizontal = ('students',)
    ordering = ('name',)
