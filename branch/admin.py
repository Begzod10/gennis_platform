from django.contrib import admin

from .models import Branch


# Register the Branch model
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'number', 'location', 'location_text', 'map_link', 'code',
        'phone_number', 'director_fio', 'location_type', 'district',
        'bank_sheet', 'inn', 'bank', 'mfo', 'campus_name',
        'address', 'year', 'old_id'
    )
    search_fields = (
        'name', 'location__name', 'director_fio', 'district',
        'phone_number', 'campus_name', 'address', 'inn', 'bank', 'code'
    )
    list_filter = (
        'location', 'location_type', 'district', 'year'
    )
    ordering = ('name',)
