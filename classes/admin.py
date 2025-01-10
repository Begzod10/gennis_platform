from django.contrib import admin

from .models import (
    ClassColors, ClassTypes, ClassNumber,
    ClassCoin, CoinInfo, StudentCoin
)


# Register the ClassColors model
@admin.register(ClassColors)
class ClassColorsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name', 'value')
    ordering = ('id',)


# Register the ClassTypes model
@admin.register(ClassTypes)
class ClassTypesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('id',)


# Register the ClassNumber model
@admin.register(ClassNumber)
class ClassNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'curriculum_hours')
    search_fields = ('number', 'class_types__name')
    filter_horizontal = ('subjects',)
    ordering = ('id',)


# Register the ClassCoin model
@admin.register(ClassCoin)
class ClassCoinAdmin(admin.ModelAdmin):
    list_display = ('group', 'total_coin', 'given_coin', 'remaining_coin', 'month_date')
    search_fields = ('group__name', 'month_date')
    list_filter = ('group', 'month_date')
    ordering = ('id',)


# Register the CoinInfo model
@admin.register(CoinInfo)
class CoinInfoAdmin(admin.ModelAdmin):
    list_display = ('value', 'reason', 'day_date', 'class_coin')
    search_fields = ('value', 'reason', 'class_coin__group__name')
    list_filter = ('day_date', 'class_coin')
    ordering = ('id',)


# Register the StudentCoin model
@admin.register(StudentCoin)
class StudentCoinAdmin(admin.ModelAdmin):
    list_display = ('value', 'class_coin', 'student')
    search_fields = ('value', 'class_coin__group__name', 'student__user__username')
    list_filter = ('class_coin', 'student')
    ordering = ('id',)
