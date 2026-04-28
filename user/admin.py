from django.contrib import admin

from .models import CustomUser, CustomAutoGroup, UserSalary, UserSalaryList


@admin.register(CustomAutoGroup)
class CustomAutoGroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'salary', 'user', 'old_id')
    search_fields = ('group__name', 'user__username')
    list_filter = ('group',)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'surname', 'branch', 'language', 'calculate_age', 'phone', 'observer')
    search_fields = ('username', 'name', 'surname', 'phone')
    list_filter = ('branch', 'language', 'observer')


@admin.register(UserSalary)
class UserSalaryAdmin(admin.ModelAdmin):
    list_display = ('user', 'permission', 'date', 'total_salary', 'taken_salary', 'remaining_salary', 'old_id')
    search_fields = ('user__username', 'permission__group__name')
    list_filter = ('permission',)


@admin.register(UserSalaryList)
class UserSalaryListAdmin(admin.ModelAdmin):
    list_display = ('user_salary', 'permission', 'payment_types', 'user', 'branch', 'salary', 'date', 'deleted')
    search_fields = ('user__username', 'branch__name')
    list_filter = ('branch', 'deleted')
