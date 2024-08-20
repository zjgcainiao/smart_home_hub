from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser
import socket
import logging
import os

logger = logging.getLogger('django.networking')

def advertise_this_project_as_service():
    # Define the properties of the service
    service_name = "SmartHomeHub._http._tcp.local."
    service_port = int(os.getenv('SERVICE_PORT', 8000))  # Get from environment variable
    service_address = socket.inet_aton(os.getenv('SERVICE_IP', '192.168.1.39')) # use local server's ip address

    # Create the service info
    service_info = ServiceInfo(
        type_=service_name,
        name=f"Automan Smart Home Hub @ {socket.gethostname()}._http._tcp.local.",
        address=service_address,
        port=service_port,
        properties={},
    )

    # Create a Zeroconf instance and register the service
    zeroconf = Zeroconf()
    logger.info(f"Registering service {service_name}")
    print(f"Registering service {service_name}")
    try:
        zeroconf.register_service(service_info)
    except Exception as e:
        logger.error(f"Failed to register service: {e}")
        return

    try:
        input("Press enter to unregister the service\n")
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(service_info)
        zeroconf.close()

    try:
        # Service runs indefinitely until interrupted
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Unregistering...")
        try:
            zeroconf.unregister_service(service_info)
            zeroconf.close()
        except Exception as e:
            logger.error(f"Failed to unregister service: {e}")

if __name__ == "__main__":
    advertise_this_project_as_service()



class NetworkMapper:
    def __init__(self):
        self.services = {}

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            self.services[name] = info
            print(f"Service {name} added, service info: {info}")

    def remove_service(self, zeroconf, type, name):
        self.services.pop(name, None)
        print(f"Service {name} removed")

def map_network():
    zeroconf = Zeroconf()
    listener = NetworkMapper()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)

    try:
        input("Press enter to exit\n")
    finally:
        zeroconf.close()

if __name__ == "__main__":
    map_network()
