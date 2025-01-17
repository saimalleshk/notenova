from django.apps import AppConfig

class AppnotenovaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appnotenova'

    def ready(self):
        import appnotenova.signals
