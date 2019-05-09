from qhue import Bridge

from django.utils import timezone
from .models import MonitorLights, MonitorBridge
# HUE_BRIDGE_USERNAME='f3o4eLryVkXDCuJ5OVXAatxLsdrZdh-Y-HlwLYA'
# HUE_BRIDGE_IP_ADDRESS='192.168.0.2'
import os
from dotenv import load_dotenv
load_dotenv()
HUE_BRIDGE_USERNAME=os.getenv("HUE_BRIDGE_USERNAME")
HUE_BRIDGE_IP_ADDRESS=os.getenv("HUE_BRIDGE_IP_ADDRESS")


b = Bridge(HUE_BRIDGE_IP_ADDRESS, HUE_BRIDGE_USERNAME)
b.connect() # if b is using phue library
# get the lights
lights = b.lights

config_b=b.config()
lights=b.lights()

import datetime
bridge_ins=MonitorBridge(
    bridge_name=config_b['name'],
    bridge_ip_address='192.168.0.2',
    bridge_localtime=datetime.datetime.now(),
    bridge_timezone='America/Los_Angeles',
    bridge_unique_id=config_b['bridgeid']
)


