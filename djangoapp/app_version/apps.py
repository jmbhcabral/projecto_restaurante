# djangoapp/app_version/apps.py
from django.apps import AppConfig


class AppVersionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangoapp.app_version"
