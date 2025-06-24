# from django.contrib import admin
#
# from .models import Lead, LeadCall
#
#
# # Register the Lead model
# @admin.register(Lead)
# class LeadAdmin(admin.ModelAdmin):
#     list_display = ('name', 'phone', 'subject', 'branch')
#     search_fields = ('name', 'phone', 'subject__name', 'branch__name')
#     list_filter = ('subject', 'branch')
#     ordering = ('name',)
#
#
# # Register the LeadCall model
# @admin.register(LeadCall)
# class LeadCallAdmin(admin.ModelAdmin):
#     list_display = ('lead', 'created', 'delay', 'comment')
#     search_fields = ('lead__name', 'lead__phone', 'comment')
#     list_filter = ('created', 'delay', 'lead__subject', 'lead__branch')
#     ordering = ('-created',)
