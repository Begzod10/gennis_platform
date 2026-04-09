from django.contrib import admin

from .models import Years, Month, Day, TypeDay


# Register the Years model
@admin.register(Years)
class YearsAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)
    ordering = ('id',)


# Register the Month model
@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ('month_number', 'month_name', 'years')
    search_fields = ('month_name', 'years__year')
    list_filter = ('years',)
    ordering = ('id',)


# Register the Day model
@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('day_number', 'day_name', 'month', 'year', 'type_id')
    search_fields = ('day_name', 'month__month_name', 'year__year', 'type_id__type')
    list_filter = ('month', 'year', 'type_id')
    ordering = ('id',)


# Register the TypeDay model
@admin.register(TypeDay)
class TypeDayAdmin(admin.ModelAdmin):
    list_display = ('type', 'color')
    search_fields = ('type',)
    ordering = ('id',)
