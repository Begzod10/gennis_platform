from django.contrib import admin

from .models import Language


# Register the Language model
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'old_id')
    search_fields = ('name',)
    ordering = ('name',)
