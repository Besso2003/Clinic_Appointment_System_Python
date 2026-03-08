from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    name = 'scheduling'

    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()