from django.apps import AppConfig


class AttendancesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendances'

    def ready(self):
        import attendances.signals
