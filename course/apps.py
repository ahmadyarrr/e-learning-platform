from django.apps import AppConfig
from django.core.cache import cache


class CourseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'course'
    cache.clear()