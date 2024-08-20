# management/commands/initialize_hue_data.py

from django.core.management.base import BaseCommand
from philips_hue.models import HueLight

import requests

class Command(BaseCommand):
    help = 'Initialize data from the Hue Bridge'

    def handle(self, *args, **kwargs):
        ip_address = find_hue_bridge_ip()  # Implement this function to discover the Hue Bridge
        app_key = 'your_hue_application_key'
        self.fetch_and_store_data(ip_address, app_key)

    def fetch_and_store_data(self, ip_address, app_key):
        endpoints = [
            'device', 'light', 'bridge', 'bridge_home',
            'device_power', 'motion','sensor', 'group',
            'homekit',
        ]
        headers = {'hue-application-key': app_key}
        
        for endpoint in endpoints:
            response = requests.get(f'https://{ip_address}/clip/v2/resource/{endpoint}', headers=headers, verify=False)
            data = response.json()
            
            # Process and store data
            # For example, if fetching lights:
            if endpoint == 'light':
                for light_data in data['data']:
                    HueLight.objects.update_or_create(
                        id=light_data['id'],
                        defaults={
                            'id_v1': light_data['id_v1'],
                            # ... other fields ...
                        }
                    )
