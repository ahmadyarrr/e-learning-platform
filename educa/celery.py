import os
from celery  import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE',"educa.settings")

cel_app = Celery("educa")
cel_app.config_from_object('django.conf:settings',namespace="CELERY")
cel_app.autodiscover_tasks()


