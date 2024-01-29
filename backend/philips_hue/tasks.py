# tasks.py
import requests
from django.core.cache import cache
from celery import shared_task
from decouple import config 
from philips_hue.utilities import get_bridge_info_from_mdns
import logging
from philips_hue.models import MonitorBridge, MonitorLights, Group, HueLight, HueRoom, HueDevice
from django.conf import settings
from celery.utils.log import get_task_logger
from django.core.exceptions import ValidationError
import json
from django.db import transaction, IntegrityError


logger = get_task_logger('django')

# fetch from the Hue API V2 URL pattern: https://<bridge_ip_address>/clip/v2/resource/<endpoint>; 
# or if left blank, https://<bridge_ip_address>/clip/v2/resource by default
@shared_task
def fetch_resource_endpoint_task(endpoint=''):
    """
    Fetches the resource endpoint data from the Philips Hue API V2.

    Args:
        endpoint (str, optional): The specific endpoint to fetch data from. Defaults to ''.

    Returns:
        dict: The fetched data from the resource endpoint, or None if an error occurred.
    """
    # Validate the endpoint
    valid_endpoints = ["light", "device", "room",'grouped_light' "scene", "zone", "entertainment"]
    if endpoint and endpoint not in valid_endpoints:
        raise ValueError(f"Invalid endpoint: {endpoint}. Endpoint must be one of {valid_endpoints}.")

    # Attempt to fetch bridge info
    bridge_info = get_bridge_info_from_mdns()
    if not bridge_info or 'internalipaddress' not in bridge_info:
        logger.error("Failed to fetch the bridge IP address.")
        return None

    ip_address = bridge_info['internalipaddress']
    hue_bridge_username = settings.HUE_BRIDGE_USERNAME2

    headers = {'hue-application-key': hue_bridge_username}

    # Construct the URL based on the endpoint
    if not endpoint:
        url = f"https://{ip_address}/clip/v2/resource"
    else:
        url = f"https://{ip_address}/clip/v2/resource/{endpoint}"

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            cache_key = f"hue_{endpoint}s" if endpoint else "hue_resource"
            cache.set(cache_key, data, timeout=60*60*24*7)  # cache for 7 days
            return data
        else:
            error_message = response.json().get('errors', 'Unknown error')
            logger.error(f"Failed to fetch data from the Hue API V2 url {url}. Status code: {response.status_code}. Error message: {error_message}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while fetching data from {url}: {str(e)}")
        return None

# fetch a specific resource (light, room, device, etc.) 
# from the Hue API V2 URL pattern: https://<bridge_ip_address>/clip/v2/resource/<endpoint>/<identifier>
@shared_task
def fetch_resource_endpoint_detail_task(endpoint, identifier):
    """
    Fetches the resource endpoint data from the Philips Hue API V2.

    Args:
        endpoint (str, optional): The specific endpoint to fetch data from. Defaults to ''.

    Returns:
        dict: The fetched data from the resource endpoint, or None if an error occurred.
    """
    # Validate the endpoint
    valid_endpoints = ["light", "device", "room",'grouped_light', "scene", "zone", "entertainment"]
    if endpoint and endpoint not in valid_endpoints:
        raise ValueError(f"Invalid endpoint: {endpoint}. Endpoint must be one of {valid_endpoints}.")

    # Attempt to fetch bridge info
    bridge_info = get_bridge_info_from_mdns()
    if not bridge_info or 'internalipaddress' not in bridge_info:
        logger.error("Failed to fetch the bridge IP address.")
        return None

    ip_address = bridge_info['internalipaddress']
    hue_bridge_username = settings.HUE_BRIDGE_USERNAME2

    headers = {'hue-application-key': hue_bridge_username}

    # Construct the URL based on the endpoint
    if not endpoint or not identifier:
        AttributeError("endpoint and identifier must be provided")
        logger.error("endpoint and identifier must be provided")
    else:
        url = f"https://{ip_address}/clip/v2/resource/{endpoint}/{identifier}"

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            if not data['errors']:
                data = data['data'] # return a list
                cache_key = f"hue_{endpoint}_uid_{identifier}"
                cache.set(cache_key, data, timeout=60*10)  # cache for 10 minutes
            return data
        else:
            error_message = response.json().get('errors', 'Unknown error')
            logger.error(f"Failed to fetch data from the Hue API V2 url {url}. Status code: {response.status_code}. Error message: {error_message}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while fetching data from {url}: {str(e)}")
        return None


@shared_task
# PUT to set light and grouped_light resouces by its uuid (`rid`)
def control_light_resource(endpoint, uuid, data):
    """
    Controls a light or grouped light resource.

    :param ip_address: IP address of the Hue Bridge
    :param endpoint: 'light' or 'grouped_light'
    :param uuid: UUID of the resource to control
    :param data: Data payload for the PUT request (e.g., '{"dimming": {"brightness": 100}}')
    :return: Response data or None
    """
    if endpoint not in ['light', 'grouped_light']:
        raise ValueError("Invalid endpoint. Must be 'light' or 'grouped_light'.")
    
    # Attempt to fetch bridge info
    bridge_info = get_bridge_info_from_mdns()
    if not bridge_info or 'internalipaddress' not in bridge_info:
        logger.error("Failed to fetch the bridge IP address.")
        return None

    ip_address = bridge_info['internalipaddress']
    hue_bridge_username = settings.HUE_BRIDGE_USERNAME2

# https://192.168.1.43/clip/v2/resource/grouped_light/01904780-2d89-4793-9424-ed5656ad20d4
    url = f"https://{ip_address}/clip/v2/resource/{endpoint}/{uuid}"
    hue_bridge_username = config('HUE_BRIDGE_USERNAME2')
    headers = {
        'hue-application-key': hue_bridge_username,
        'Content-Type': 'application/json'
    }

    try:
        
        # Determine which part of the data to send based on 'on' status. Then convert to JSON-like string
        if 'on' in data and data['on'].get('on') is False:
            json_data = json.dumps({'on': {'on': False}})
        elif 'dimming' in data:
            # Ensure brightness is an integer
            brightness = int(data['dimming'].get('brightness', 0))
            json_data = json.dumps({'on': {'on': True}}, {'dimming': {'brightness': brightness}})
        else:
            logger.error("No valid control data provided.")
            return {'status': 'error', 'message': "No valid control data"}


        response = requests.put(url, headers=headers, data=json_data, verify=False)
        if response.status_code == 200:
            return response.json()['data']
        else:
            logger.error(f"Failed to control light resource at {url}. Status code: {response.status_code}. Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while controlling light resource at {url}: {str(e)}")
        return None


@shared_task
def save_lights_task(lights_data=[]):
    if not lights_data:
        fetch_resource_endpoint_task(endpoint='light')
        lights_data = cache.get('hue_lights')['data']
    results = []
    for light_data in lights_data:
        try:
            with transaction.atomic():
                light, created = HueLight.objects.update_or_create(
                    uuid=light_data['id'],
                    defaults={
                        'id_v1': light_data.get('id_v1', ''),
                        'owner': light_data.get('owner', {}),
                        'metadata': light_data.get('metadata', {}),
                        'product_data': light_data.get('product_data', {}),
                        'identify': light_data.get('identify', {}),
                        'signaling': light_data.get('signaling', {}),
                        'type': light_data.get('type', ''),
                        'powerup': light_data.get('powerup', {}),
                        'state': {
                            'on': light_data.get('on', {}),
                            'dimming': light_data.get('dimming', {}),
                            'color': light_data.get('color', {}),
                            'color_temperature': light_data.get('color_temperature', {}),
                            'dimming_delta': light_data.get('dimming_delta', {}),
                            'color_temperature_delta': light_data.get('color_temperature_delta', {}),
                            'dynamics': light_data.get('dynamics', {}),
                            'signaling': light_data.get('signaling', {}),  # the same as the signaling field in the root object
                            'alert': light_data.get('alert', {}),
                            'effects': light_data.get('effects', {}),
                            'mode': light_data.get('mode', {}),
                            # ... include other fields as needed
                        },
                    }
                )
                results.append({'status': 'success', 'uuid': light_data['id'],'v1_id': light_data.get('id_v1', '')})
        except ValidationError as e:
            logger.error(f'Data validation error for light {light_data["id"]}: {e}')
            results.append({'status': 'error', 'uuid': light_data['id'], 'error': str(e)})
        except IntegrityError as e:
            logger.error(f'Integrity error for light {light_data["id"]}: {e}')
            input('press enter to continue')
            results.append({'status': 'error', 'uuid': light_data['id'], 'error': 'Duplicate key value violates unique constraint'})
        except Exception as e:
            logger.error(f'Unexpected error saving light data for light {light_data["id"]}: {e}')
            results.append({'status': 'error', 'uuid': light_data['id'], 'error': str(e)})        

    logger.info(f'completed saving light data...full result: {results}')
    
    return results


@shared_task
def save_rooms_task(rooms_data=[]):
    if not rooms_data:
        fetch_resource_endpoint_task(endpoint='room')
        rooms_data = cache.get('hue_rooms')['data']
    results = []
    for room_data in rooms_data:
        try:
            with transaction.atomic():
                room, created = HueRoom.objects.update_or_create(
                    uuid=room_data['id'],
                    defaults={
                        'id_v1': room_data.get('id_v1', ''),
                        'children': room_data.get('children', []),
                        'services': room_data.get('services', []),
                        'metadata': room_data.get('metadata', {}),
                        'type': room_data.get('type', ''),
                    }
                )
                results.append({'status': 'success', 'id': room_data['id']})
        except Exception as e:
            results.append({'status': 'error', 'id': room_data['id'], 'error': str(e)})
    return results

@shared_task
def save_devices_task(devices_data=[]):
    if not devices_data:
        fetch_resource_endpoint_task(endpoint='device')
        devices_data = cache.get('hue_devices')['data']
    results = []
    for device_data in devices_data:
        try:
            with transaction.atomic():
                device, created = HueDevice.objects.update_or_create(
                    uuid=device_data['id'],
                    defaults={
                        'id_v1': device_data.get('id_v1', ''),
                        'product_data': device_data.get('product_data', {}),
                        'metadata': device_data.get('metadata', {}),
                        'identify': device_data.get('identify', {}),
                        'services': device_data.get('services', []),
                        'type': device_data.get('type', ''),
                    }
                )
                results.append({'status': 'success', 'id': device_data['id']})
        except Exception as e:
            results.append({'status': 'error', 'id': device_data['id'], 'error': str(e)})
    return results