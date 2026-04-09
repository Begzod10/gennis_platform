from django.contrib import admin

from .models import Room, RoomImages, RoomSubject


# Register the Room model
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'seats_number', 'branch', 'electronic_board', 'deleted', 'old_id')
    search_fields = ('name', 'branch__name')
    list_filter = ('branch', 'electronic_board', 'deleted')
    ordering = ('name',)


# Register the RoomImages model
@admin.register(RoomImages)
class RoomImagesAdmin(admin.ModelAdmin):
    list_display = ('room', 'image', 'old_id')
    search_fields = ('room__name',)
    list_filter = ('room',)


# Register the RoomSubject model
@admin.register(RoomSubject)
class RoomSubjectAdmin(admin.ModelAdmin):
    list_display = ('room', 'subject')
    search_fields = ('room__name', 'subject__name')
    list_filter = ('room', 'subject')
