from django.contrib import admin

from .models import System


# Register the System model
@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'number')
    search_fields = ('name',)
    ordering = ('name',)
