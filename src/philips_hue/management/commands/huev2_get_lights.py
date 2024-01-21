import requests
from decouple import config
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Get lights information from the Philips Hue Bridge'

    def handle(self, *args, **options):
        # Your Philips Hue Bridge IP and the application key
        bridge_ip = config('HUE_BRIDGE_IP_ADDRESS')
        application_key = config('HUE_APPLICATION_ID')

        # The URL for the lights endpoint
        url = f'https://{bridge_ip}/clip/v2/resource/light'

        # The headers including the hue-application-key
        headers = {
            'hue-application-key': application_key
        }

        # Perform the GET request
        # Note: Setting verify=False bypasses SSL certificate verification. 
        # It's not recommended for production use unless you're sure about the security of your network.
        response = requests.get(url, headers=headers, verify=False)

        # Check the response status code
        if response.status_code == 200:
            # If the request was successful, print the response text (JSON data)
            self.stdout.write(self.style.SUCCESS("Successfully retrieved lights information."))
            self.stdout.write(response.text)
        else:
            # If the request failed, print the status code and response content
            self.stdout.write(self.style.ERROR(f"Failed to retrieve lights information. Status code: {response.status_code}"))
            self.stdout.write("Response: " + str(response.content))
