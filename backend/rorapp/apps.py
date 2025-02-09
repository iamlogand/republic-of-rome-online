from django.apps import AppConfig


class RorappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rorapp"

    def ready(self):
        import rorapp.signals