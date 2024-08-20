from django.apps import AppConfig


class PhilipsHueConfig(AppConfig):
    name = 'philips_hue'

    def ready(self):
        from philips_hue.periodic_crontab_tasks import create_periodic_tasks
        # create_periodic_tasks()
