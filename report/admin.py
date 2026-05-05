from django.contrib import admin

from .models import AdminRequest, RequestComment

class RequestCommentInline(admin.TabularInline):
    model = RequestComment
    extra = 1

@admin.register(AdminRequest)
class AdminRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'user', 'deadline', 'created_at')
    list_filter = ('branch', 'user', 'deadline')
    search_fields = ('name', 'description')
    inlines = [RequestCommentInline]

@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    list_display = ('request', 'user', 'created_at')
    list_filter = ('user', 'created_at')


