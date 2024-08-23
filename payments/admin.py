from django.contrib import admin

from .models import PaymentTypes


# Register the PaymentTypes model
@admin.register(PaymentTypes)
class PaymentTypesAdmin(admin.ModelAdmin):
    list_display = ('name', 'old_id')
    search_fields = ('name',)
    ordering = ('name',)
