# Print all non-special attributes and their values
import json
import requests
from huesdk import Discover, Hue
# from decouple import config, Csv
import logging
from dotenv import load_dotenv
from django.db import transaction
from philips_hue.models import MonitorBridge, MonitorLights, Group
from django.utils import timezone
from django.utils import timezone
import socket
from zeroconf import ServiceBrowser, Zeroconf
from philips_hue.zeroconf_listener import HueListener
from django.conf import settings

logger = logging.getLogger('django')

def get_attributes(object):
    regular_methods = {}
    special_methods = {}
    
    for attribute in dir(object):
        attr_value = getattr(object, attribute)
        if attribute.startswith('__') and attribute.endswith('__'):
            # It's a special method or attribute
            special_methods[attribute] = repr(attr_value)
        else:
            # It's a regular method or attribute
            regular_methods[attribute] = repr(attr_value)
    
    # Nesting regular_methods and special_methods under their respective keys
    all_attributes = {
        "regular_methods": regular_methods,
        "special_methods": special_methods
    }
    return all_attributes  # for Python dictionary
    # return json.dumps(all_attributes, indent=4)  # for JSON string with pretty formatting

import time

# search mdns for the bridge info. usually there is only one bridge in the system.

def get_bridge_info_from_mdns():
    timeout = 10 # seconds
    zeroconf = Zeroconf()
    listener = HueListener()
    browser = ServiceBrowser(zeroconf, "_hue._tcp.local.", listener)

    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if listener.device_info or elapsed_time > timeout:
            break
        time.sleep(0.1)  # Sleep for a short time to prevent a busy-wait loop

    zeroconf.close()
    return listener.device_info
# the service_info (input) is a ServiceInfo object from the zeroconf library


# update or create a bridge based on the unqiue id.
def update_or_create_bridge_in_system():
                   
    monitor_bridges = []  # List to store MonitorBridge instances

    # try:
    #     discover = Discover()
    #     raw_bridges = discover.find_hue_bridge_mdns(timeout=10)
    #     raw_bridges=json.loads(raw_bridges)
    #     # If local discovery fails, fetch bridge info from the Philips Hue discovery API
    #     if not raw_bridges:
    #         response = requests.get("https://discovery.meethue.com")
    #         if response.status_code == 200:
    #             raw_bridges = response.json()
    #         else:
    #             # https://discovery.meethue.com/ is the equivalent of the following code
    #             logging.error(f"Failed to fetch data from https://discovery.meethue.com. Status code: {response.status_code}")
    #             return None
    #             # update or create MonitorBridge instance

    raw_bridges = [get_bridge_info_from_mdns()]

    with transaction.atomic():
            # Iterate through the discovered bridges
            for bridge_info in raw_bridges:
                # Use update_or_create to update an existing instance or create a new one
                monitor_bridge, created = MonitorBridge.objects.update_or_create(
                    bridge_unique_id=bridge_info["id"],
                    defaults={
                        'bridge_name': bridge_info["name"],
                        'bridge_ip_address': bridge_info["internalipaddress"],
                        'bridge_localtime': timezone.now(),  # Set current time for bridge_localtime
                        'bridge_timezone': timezone.get_current_timezone()  # Fetch the system's timezone dynamically
                    }
                )
                # Add the MonitorBridge instance to the list
                monitor_bridges.append(monitor_bridge)
                # The 'created' variable is a boolean that is True if a new instance was created
                if created:
                   logger.info(f"Created new MonitorBridge: {monitor_bridge.bridge_name}")
                else:
                    logger.info(f"Updated existing MonitorBridge: {monitor_bridge.bridge_name}")
    
    return monitor_bridges
    # except Exception as e:
    #     logging.error(f"An error occurred while syncing lights with the database: {str(e)}")
    #     return []


# fetch the resources 
def fetch_hue_resources_manually():
    try:
        ip_address = get_bridge_info_from_mdns()['internalipaddress']
        try:
            hue_bridge_username = settings.HUE_BRIDGE_USERNAME2
        except AttributeError:
            logger.info("HUE_BRIDGE_USERNAME not found, trying HUE_BRIDGE_USERNAME2")
            hue_bridge_username = settings.HUE_BRIDGE_USERNAME

        url = f"https://{ip_address}/clip/v2/resource"
        headers = {'hue-application-key': hue_bridge_username}

        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Error during requests to {url}: {req_err}")

    except Exception as e:
        logger.error(f"An error occurred while fetching the bridge IP address or username: {str(e)}")
        return None



# def sync_groups_with_db():
#     """
#     Syncs the Hue groups with the Group model in the database.

#     This function establishes a connection to the Hue bridge, fetches the groups from the bridge,
#     and updates or creates corresponding Group instances in the database.

#     Returns:
#         A list of Group instances that have been synced with the database.
#     """
#     try:
#         # Establish a connection to the Hue bridge
#         hue = get_hue_connection()
#         if not hue:
#             logging.error("Unable to establish a connection to the Hue bridge.")
#             return []

#         # Fetch groups from the Hue bridge
#         raw_groups = hue.get_groups()  # Adjust based on your Hue SDK or API
#         print(f'here is how raw_groups looks like: {raw_groups}')
#         # Sync Hue groups with the Group model
#         groups = []
#         with transaction.atomic():
#             for hue_group in raw_groups:
#                 group, created = Group.objects.update_or_create(
#                     group_id=hue_group.id_,  # Assuming hue_group has an attribute 'id_'
#                     defaults={
#                         'name': hue_group.name,  # Maps to 'name'
#                         'is_on': hue_group.is_on,  # Maps to 'is_on'
#                         'brightness': hue_group.bri,  # Maps to 'bri'
#                         'hue': hue_group.hue,  # Maps to 'hue'
#                         'saturation': hue_group.sat,  # Maps to 'sat'
#                     }
#                 )
#                 groups.append(group)
#                 # Log creation or update of the Group instance
#                 if created:
#                     logging.info(f"Created new Group: {group.name}")
#                 else:
#                     logging.info(f"Updated existing Group: {group.name}")
        
#         return groups

#     except Exception as e:
#         logging.error(f"An error occurred while syncing groups with the database: {str(e)}")
#         return []