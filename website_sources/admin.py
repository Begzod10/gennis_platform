from django.contrib import admin

from website_sources.models import (
    ComponentDefinition,
    DynamicForm,
    GlobalSetting,
    MediaAsset,
    Menu,
    Page,
    PageSection,
    ReusableBlock,
    ThemeSetting,
)


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    fields = ('section_id', 'component', 'parent', 'sort_order', 'is_active', 'visibility')
    ordering = ('sort_order', 'id')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'locale', 'status', 'branch', 'version', 'updated_at')
    list_filter = ('status', 'locale', 'branch')
    search_fields = ('slug', 'title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PageSectionInline]


@admin.register(ComponentDefinition)
class ComponentDefinitionAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'is_layout', 'is_active')
    list_filter = ('is_layout', 'is_active')
    search_fields = ('key', 'name')
    prepopulated_fields = {'key': ('name',)}


@admin.register(ThemeSetting)
class ThemeSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode', 'branch', 'is_default', 'updated_at')
    list_filter = ('mode', 'is_default', 'branch')
    search_fields = ('name',)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'branch', 'is_active')
    list_filter = ('is_active', 'branch')
    search_fields = ('key', 'name')
    prepopulated_fields = {'key': ('name',)}


@admin.register(ReusableBlock)
class ReusableBlockAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'branch', 'is_active')
    list_filter = ('is_active', 'branch')
    search_fields = ('key', 'name')
    prepopulated_fields = {'key': ('name',)}


@admin.register(DynamicForm)
class DynamicFormAdmin(admin.ModelAdmin):
    list_display = ('key', 'title', 'branch', 'is_active')
    list_filter = ('is_active', 'branch')
    search_fields = ('key', 'title')
    prepopulated_fields = {'key': ('title',)}


admin.site.register(MediaAsset)
admin.site.register(GlobalSetting)
