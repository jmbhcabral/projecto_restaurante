import os

from celery import Celery  # type: ignore

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoapp.project.settings")

app = Celery("project")  # type: ignore
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()