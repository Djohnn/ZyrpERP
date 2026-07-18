from django.apps import AppConfig


class FiscalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fiscal'

    def ready(self):
        from fiscal import tasks  # noqa: F401
