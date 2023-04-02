from django.apps import AppConfig


class DealsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deals_app'

    def ready(self):
        import deals_app.signals

