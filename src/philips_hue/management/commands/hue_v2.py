# your_app/management/commands/hue_v2.py
import requests
from decouple import config
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Get the Hue Application ID from the Philips Hue Bridge'

    def handle(self, *args, **options):
        # Your Philips Hue Bridge IP and the application key (username from v1)
        bridge_ip = config('HUE_BRIDGE_IP_ADDRESS')
        application_key = config('HUE_BRIDGE_ID')

        # The URL for the /auth/v1 endpoint
        url = f'http://{bridge_ip}/api/auth/v1'

        # The headers including the hue-application-key
        headers = {
            'hue-application-key': application_key
        }

        # Perform the GET request
        response = requests.get(url, headers=headers)

        # Check the response status code
        if response.status_code == 200:
            # If the request was successful, print the response headers
            self.stdout.write(self.style.SUCCESS("Successfully authenticated."))
            self.stdout.write("Response Headers: " + str(response.headers))
        else:
            # If the request failed, print the status code and response content
            self.stdout.write(self.style.ERROR(f"Failed to authenticate. Status code: {response.status_code}"))
            self.stdout.write("Response: " + str(response.content))

        # If the 'hue-application-id' is present in the response headers, print it
        if 'hue-application-id' in response.headers:
            self.stdout.write("Your Application ID: " + response.headers['hue-application-id'])
