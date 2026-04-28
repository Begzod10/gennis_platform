from django.contrib import admin

from .models import ObservationInfo, ObservationOptions, ObservationDay, ObservationStatistics


# Register the ObservationInfo model
@admin.register(ObservationInfo)
class ObservationInfoAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ('id',)


# Register the ObservationOptions model
@admin.register(ObservationOptions)
class ObservationOptionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name',)
    ordering = ('id',)


# Register the ObservationDay model
@admin.register(ObservationDay)
class ObservationDayAdmin(admin.ModelAdmin):
    list_display = ('day', 'average', 'comment', 'user', 'group', 'teacher', 'deleted')
    search_fields = ('comment', 'user__username', 'group__name', 'teacher__user__username')
    list_filter = ('day', 'group', 'teacher', 'deleted')
    date_hierarchy = 'day'
    ordering = ('id',)


# Register the ObservationStatistics model
@admin.register(ObservationStatistics)
class ObservationStatisticsAdmin(admin.ModelAdmin):
    list_display = ('comment', 'observation_day', 'observation_info', 'observation_option')
    search_fields = ('comment', 'observation_day__comment', 'observation_info__title', 'observation_option__name')
    list_filter = ('observation_day', 'observation_info', 'observation_option')
    ordering = ('id',)
