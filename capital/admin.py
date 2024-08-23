from django.contrib import admin

from .models import CapitalCategory, Capital, CapitalTerm, OldCapital


# Register the CapitalCategory model
@admin.register(CapitalCategory)
class CapitalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_number', 'img')
    search_fields = ('name', 'id_number')
    ordering = ('id',)


# Register the Capital model
@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'id_number', 'price', 'total_down_cost', 'added_date',
        'term', 'curriculum_hours', 'branch', 'payment_type', 'category', 'deleted'
    )
    search_fields = ('name', 'id_number', 'branch__name', 'payment_type__name', 'category__name')
    list_filter = ('branch', 'payment_type', 'category', 'deleted')
    ordering = ('id',)


# Register the CapitalTerm model
@admin.register(CapitalTerm)
class CapitalTermAdmin(admin.ModelAdmin):
    list_display = ('capital', 'down_cost', 'month_date')
    search_fields = ('capital__name',)
    list_filter = ('month_date', 'capital')
    ordering = ('id',)


# Register the OldCapital model
@admin.register(OldCapital)
class OldCapitalAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'by_who', 'added_date', 'branch',
        'payment_type', 'old_id'
    )
    search_fields = ('name', 'by_who__username', 'branch__name', 'payment_type__name')
    list_filter = ('added_date', 'branch', 'payment_type')
    ordering = ('id',)
