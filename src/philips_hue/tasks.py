# tasks.py
import requests
from django.core.cache import cache
from celery import shared_task
from decouple import config 
from philips_hue.utilities import get_bridge_info_from_mdns
import logging

logger = logging.getLogger('django')


@shared_task
def fetch_hue_data():
    bridge= get_bridge_info_from_mdns()
    ip_address = bridge['internalupaddress']
    logger.info(f'running fetch_hue_data for {ip_address}')
    app_key = config('HUE_BRIDGE_USERNAME')
    url = f"https://{ip_address}/clip/v2/resource"
    headers = {'hue-application-key': app_key}
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    cache.set('hue_data', data, timeout=None)  # Store in Redis without an expiry
