from zeroconf import ServiceBrowser, Zeroconf
import socket
from typing import cast
# from philips_hue.utilities import parse_bridge_info_in_mdns
from typing import cast

# class MyListener:
  
#     def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
#         print(f"Service {name} updated")
        
#     def remove_service(self, zeroconf, type, name):
#         print(f"Service {name} removed")

#     def add_service(self, zeroconf, type, name):
#         info = zeroconf.get_service_info(type, name)
#         if info:
#             print(f"Service {name} added, service info: {info}")
#             bridge_info = parse_bridge_info_in_mdns(info)
#             print(f"Parsed Bridge Info: {bridge_info}")
#             # inet_ntoa converts an IP address from network byte order (a string of binary data) to the standard dotted-quad string notation (e.g., "192.0.2.0").
#             addresses = ["%s:%d" % (socket.inet_ntoa(addr), cast(int, info.port)) for addr in info.addresses]
#             print("Addresses: %s" % ", ".join(addresses))


class HueListener:
    def __init__(self):
        self.device_info = {}

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            print(f"Service {name} added, service info: {info}")
            # Parse service info and store in device_info
            self.device_info = self.parse_bridge_info(info)

    def parse_bridge_info(self, service_info):
        # Extracting the IP address
        ip_address = socket.inet_ntoa(service_info.addresses[0])

        # Extracting the bridge ID from the properties
        bridge_id_raw = service_info.properties.get(b'bridgeid', b'')
        bridge_id = bridge_id_raw.decode('utf-8') if bridge_id_raw else ''

        # Extracting the name from the service name
        name_raw = service_info.name
        name = name_raw.split('.')[0] if name_raw else ''

        # Extracting the port
        port = service_info.port

        # Extracting the model_id from the properties
        model_id_raw = service_info.properties.get(b'modelid', b'')
        model_id = model_id_raw.decode('utf-8') if model_id_raw else ''

        return {
            'internalipaddress': ip_address,
            'id': bridge_id,
            'name': name,
            'port': port,
            'model_id': model_id
        }
