from django.contrib import admin
from website_sources.models import (
    Category, News, Admission, ContactMessage, JobPosition, CareerApplication, TalentPool, PageSection
)

@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('page', 'section_id', 'branch', 'updated_at')
    list_filter = ('page', 'branch')
    search_fields = ('page', 'section_id')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch')
    search_fields = ('name',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published', 'date', 'branch')
    list_filter = ('published', 'category', 'branch')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'student_name', 'status', 'grade', 'branch', 'created_at')
    list_filter = ('status', 'grade', 'branch')
    search_fields = ('application_id', 'student_name', 'phone')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'branch', 'created_at')
    list_filter = ('status', 'branch')
    search_fields = ('name', 'email', 'message')

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'is_active', 'branch', 'deadline')
    list_filter = ('type', 'is_active', 'branch')
    search_fields = ('title', 'description')

@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'name', 'position', 'status', 'branch', 'created_at')
    list_filter = ('status', 'branch')
    search_fields = ('application_id', 'name', 'email')

@admin.register(TalentPool)
class TalentPoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'expertise', 'branch', 'created_at')
    list_filter = ('branch',)
    search_fields = ('name', 'email', 'expertise')
