from django.apps import AppConfig
from django.core.signals import request_finished


class CoreConfig(AppConfig):
    name = 'core'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """Register application signals"""
        from .helpers.signals import update_user_status

        request_finished.connect(update_user_status)
