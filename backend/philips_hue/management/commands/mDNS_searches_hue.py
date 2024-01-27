import logging
from django.core.management.base import BaseCommand
from zeroconf import ServiceBrowser, Zeroconf
from philips_hue.zeroconf_listener import MyListener


# logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Discover Philips Hue Bridges on the local network using mDNS.

    This command initiates a discovery process to find Philips Hue Bridges
    on the local network using mDNS (Multicast DNS) protocol. It listens for
    Hue Bridge services and displays the discovered bridges.

    Usage: python manage.py mDNS_searches_hue

    Press enter to stop the discovery process.
    """

    help = 'Discover Philips Hue Bridges on the local network using mDNS'

    def handle(self, *args, **options):
        try:
            zeroconf = Zeroconf()
            listener = MyListener()
            browser = ServiceBrowser(zeroconf, "_hue._tcp.local.", listener)
            input("Press enter to stop discovery...\n\n")
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Stopping discovery...'))
        except Exception as e:
            logging.error(f"An error occurred during discovery: {e}")
        finally:
            zeroconf.close()
            self.stdout.write(self.style.SUCCESS('Discovery stopped.'))