from django.apps import AppConfig, apps

from contrib.module_manager import load_modules


class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order'

    def ready(self):
        load_modules([app.name for app in apps.get_app_configs()])
