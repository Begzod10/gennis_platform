# Register your models here.
from django.contrib import admin

from .models import Overhead


# Register the Overhead model
@admin.register(Overhead)
class OverheadAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment', 'created', 'price', 'branch')
    search_fields = ('name', 'payment__name', 'branch__name')
    list_filter = ('payment', 'branch', 'created')
    ordering = ('-created',)
