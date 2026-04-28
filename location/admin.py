from django.contrib import admin

from .models import Location


# Register the Location model
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'system', 'old_id')
    search_fields = ('name', 'number', 'system__name')
    list_filter = ('system',)
    ordering = ('name',)
