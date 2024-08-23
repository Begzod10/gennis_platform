from django.contrib import admin

from .models import (
    AuthGroupSystem, Access, ManySystem,
    ManyLocation, ManyBranch, DescriptionForTable
)


# Register the AuthGroupSystem model
@admin.register(AuthGroupSystem)
class AuthGroupSystemAdmin(admin.ModelAdmin):
    list_display = ('group', 'system_id')
    search_fields = ('group__name', 'system_id__name')
    list_filter = ('system_id',)


# Register the Access model
@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'auth_group_system', 'group')
    search_fields = ('user__username', 'auth_group_system__group__name', 'group__name')
    list_filter = ('auth_group_system', 'group')


# Register the ManySystem model
@admin.register(ManySystem)
class ManySystemAdmin(admin.ModelAdmin):
    list_display = ('user', 'system')
    search_fields = ('user__username', 'system__name')
    list_filter = ('system',)


# Register the ManyLocation model
@admin.register(ManyLocation)
class ManyLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'location')
    search_fields = ('user__username', 'location__name')
    list_filter = ('location',)


# Register the ManyBranch model
@admin.register(ManyBranch)
class ManyBranchAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch')
    search_fields = ('user__username', 'branch__name')
    list_filter = ('branch',)


# Register the DescriptionForTable model
@admin.register(DescriptionForTable)
class DescriptionForTableAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'description')
    search_fields = ('table_name', 'description')
    ordering = ('table_name',)
