from django.apps import AppConfig
from smart_home_project.zeroconfi_services import advertise_this_project_as_service

class SmartHomeProjectConfig(AppConfig):
    name = 'smart_home_project'

    def ready(self):
        advertise_this_project_as_service()