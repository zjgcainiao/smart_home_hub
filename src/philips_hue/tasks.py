# tasks.py
import requests
from django.core.cache import cache
from celery import shared_task
from decouple import config 
from philips_hue.utilities import get_bridge_info_from_mdns
import logging
from philips_hue.models import MonitorBridge, MonitorLights, Group, HueLight, HueRoom

from celery.utils.log import get_task_logger
from django.core.exceptions import ValidationError

from django.db import transaction, IntegrityError


logger = get_task_logger('django')


@shared_task
def fetch_hue_resources_task():
    try:
        ip_address = get_bridge_info_from_mdns()['internalipaddress']
        hue_bridge_username = config('HUE_BRIDGE_USERNAME') 
    except Exception as e:
        logger.error(f"An error occurred while fetching the bridge ip address {ip_address} and the bridge username: {str(e)}")

        url = f"https://{ip_address}/clip/v2/resource"
        headers = {'hue-application-key': hue_bridge_username}
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data=response.json()
            cache.set('hue_resouces', data, timeout=60*60*24*7) # cache for 7 days
            return data
        else:
            # https://discovery.meethue.com/ is the equivalent of the following code
            logger.error(f"Failed to fetch data from the Hue API V2 url {url}. Status code: {response.status_code}. Error message: {data.errors}")
            return None



@shared_task
def fetch_hue_lights_task():
    try:
        ip_address = get_bridge_info_from_mdns()['internalipaddress']
        hue_bridge_username = config('HUE_BRIDGE_USERNAME') 


        url = f"https://{ip_address}/clip/v2/resource/light"
        headers = {'hue-application-key': hue_bridge_username}
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data=response.json()
            cache.set('hue_lights', data, timeout=60*60*24*7) # cache for 7 days
            return data
        else:
            # https://discovery.meethue.com/ is the equivalent of the following code
            logger.error(f"Failed to fetch data from the Hue API V2 url {url}. Status code: {response.status_code}. Error message: {data.errors}")
            return None
    except Exception as e:
        logger.error(f"An error occurred while fetching the bridge ip address {ip_address} and the bridge username: {str(e)}")

@shared_task
def save_lights_task(lights_data=[]):
    if not lights_data:
        fetch_hue_lights_task()
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
def import_rooms(rooms_data):
    results = []
    for room_data in rooms_data:
        try:
            with transaction.atomic():
                room, created = HueRoom.objects.update_or_create(
                    id=room_data['id'],
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