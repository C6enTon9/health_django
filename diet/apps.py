# diet/apps.py

from django.apps import AppConfig


class DietConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diet'
    verbose_name = '饮食管理'