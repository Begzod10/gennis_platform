from django.apps import AppConfig


class ObservationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'observation'

    def ready(self):
        import observation.signals  # noqa: F401
