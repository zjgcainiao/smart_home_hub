from zeroconf import ServiceBrowser, Zeroconf
import socket
from typing import cast
from philips_hue.utilities import parse_bridge_info_in_mdns

class MyListener:
  
    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")
        
    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            print(f"Service {name} added, service info: {info}")
            bridge_info = parse_bridge_info_in_mdns(info)
            print(f"Parsed Bridge Info: {bridge_info}")
            addresses = ["%s:%d" % (socket.inet_ntoa(addr), cast(int, info.port)) for addr in info.addresses]
            print("Addresses: %s" % ", ".join(addresses))

