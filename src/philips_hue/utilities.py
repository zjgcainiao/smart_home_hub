# Print all non-special attributes and their values
import json
import requests
from huesdk import Discover, Hue
from decouple import config, Csv
import logging
from dotenv import load_dotenv
from django.db import transaction
from philips_hue.models import MonitorBridge, MonitorLights
from django.utils import timezone

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

# Test the function with an object
# group_attributes = print_attributes(groups[1])  # Assuming 'group' is your hue "group" object
# import json

# # Convert the dictionary to a JSON string
# group_attributes_json = json.dumps(group_attributes, indent=4)
# print(group_attributes_json)



def get_hue_connection():
    """
    Retrieves the connection to the Philips Hue bridge.

    This function attempts to discover the Hue bridge locally using mDNS,
    and if that fails, it fetches bridge information from the Philips Hue
    discovery API. It then updates or creates a MonitorBridge instance in
    the database with the bridge information. Finally, it retrieves the
    stored Hue bridge username and creates a Hue connection.

    Returns:
        Hue: The connection to the Hue bridge, or None if an error occurred.
    """
   
    try:
         
        # Attempt to discover Hue Bridges locally
        discover = Discover()
        bridges = discover.find_hue_bridge_mdns(timeout=10)
        bridges=json.loads(bridges)
        # If local discovery fails, fetch bridge info from the Philips Hue discovery API
        if not bridges:
            response = requests.get("https://discovery.meethue.com")
            if response.status_code == 200:
                bridges = response.json()
            else:
                # https://discovery.meethue.com/ is the equivalent of the following code
                logging.error(f"Failed to fetch data from https://discovery.meethue.com. Status code: {response.status_code}")
                return None

        # Extract bridge IP address
        try:
            hue_bridge_ip_address = bridges[0]["internalipaddress"]
        except (IndexError, KeyError) as e:
            logging.error("No valid bridge information found.")
            return None
    
        # update or create MonitorBridge instance
        with transaction.atomic():
                # Iterate through the discovered bridges
                for bridge_info in bridges:
                    # Use update_or_create to update an existing instance or create a new one
                    monitor_bridge, created = MonitorBridge.objects.update_or_create(
                        bridge_unique_id=bridge_info["id"],
                        defaults={
                            'bridge_name': bridge_info["name"],
                            'bridge_ip_address': bridge_info["internalipaddress"],
                            'bridge_localtime': timezone.now(),  # Set current time for bridge_localtime
                            'bridge_timezone': "Americas/Chicago"  # Set your timezone or fetch it dynamically
                        }
                    )
                    # The 'created' variable is a boolean that is True if a new instance was created
                    if created:
                        print(f"Created new MonitorBridge: {monitor_bridge.bridge_name}")
                    else:
                        print(f"Updated existing MonitorBridge: {monitor_bridge.bridge_name}")
        
        
        # Retrieve stored Hue bridge username from environment variables or .env file
        hue_bridge_username = config("HUE_BRIDGE_USERNAME")

        # Create and return Hue connection
        hue = Hue(bridge_ip=hue_bridge_ip_address, username=hue_bridge_username)
        logging.info(f"Connected to Hue bridge at {hue_bridge_ip_address} with username {hue_bridge_username}")

        return hue

    except Exception as e:
        logging.error(f"An error occurred while connecting to the Hue bridge: {str(e)}")
        return None
    

def sync_lights_with_db():
    """
    Syncs the lights from the Hue bridge with the MonitorLights model in the database.

    Returns:
        A list of MonitorLights objects representing the synced lights.
    """
    try:
        # Establish a connection to the Hue bridge
        hue = get_hue_connection()
        if not hue:
            logging.error("Unable to establish a connection to the Hue bridge.")
            return []

        # Fetch lights from the Hue bridge
        hue_lights = hue.get_lights()  # Adjust based on your Hue SDK or API

        # Sync Hue lights with the MonitorLights model
        monitor_lights = []
        for hue_light in hue_lights:
            monitor_light, created = MonitorLights.objects.update_or_create(
                light_hue_id=hue_light.id_,  # Assuming hue_light has an attribute 'id_'
                defaults={
                    'light_name': hue_light.name,
                    'light_is_on': hue_light.is_on,
                    'light_bri': hue_light.bri,
                    'light_hue': hue_light.hue,
                    'light_sat': hue_light.sat,
                }
            )
            monitor_lights.append(monitor_light)
        
        return monitor_lights

    except Exception as e:
        logging.error(f"An error occurred while syncing lights with the database: {str(e)}")
        return []