from django.apps import AppConfig


class SchoolTimeTableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school_time_table'

    def ready(self):
        import school_time_table.signals  # noqa: F401
