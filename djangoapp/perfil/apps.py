# djangoapp/perfil/apps.py
from django.apps import AppConfig


class PerfilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangoapp.perfil'

    def ready(self):
        import djangoapp.perfil.signals  # noqa: F401
