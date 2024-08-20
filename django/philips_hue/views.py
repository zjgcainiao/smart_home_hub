
from django.shortcuts import render, redirect, get_object_or_404
# import the phue module to return the status of all lights
# from huesdk import Discover
from huesdk import Discover, Hue
# builds the response object
from django.http import HttpResponse
from django.http import Http404
from .models import MonitorLights
from decouple import config, Csv
from philips_hue.models import MonitorBridge, MonitorLights, Group, HueLight, HueRoom, HueDevice
from django.utils import timezone
from django.db import transaction
import os
import logging
from dotenv import load_dotenv
import json  # Import the json module
import requests
from philips_hue.utilities import get_attributes, update_or_create_bridge_in_system
from philips_hue.tasks import fetch_resource_endpoint_task, save_lights_task, save_rooms_task, save_devices_task, fetch_resource_endpoint_detail_task, control_light_resource
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


logger = logging.getLogger('django.db.backends')


def index(request):
    # bridges = get_bridges()
    # print(f'bridges are {bridges}')
    # if bridges:
    #     bridge = bridges[0]
    # else:
    #     bridge = None
    # bridge = get_bridge_info_from_mdns()
    bridges = update_or_create_bridge_in_system()
    bridge = bridges[0]
    # if bridge:
    #     bridge = MonitorBridge.objects.filter( bridge_unique_id=bridge['id'])
    print(f'bridge is {bridge}')
    logger.info(f'bridge is {bridge}')
    # bridge = MonitorBridge.objects.order_by('id').first()  # Get the first bridge if exists

    # print(discover.find_hue_bridge_mdns(timeout=10))
    if not bridge:
        # Handle the error appropriately
        context = {'error': 'Unable to find the most recent bridge.'}
    else:
        context = {'bridge': bridge}
    return render(request, 'philips_hue/index.html', context)


def get_light_list(request):
    # Sync Hue lights with the MonitorLights model

    # use the sync_lights_with_db function to sync the lights with the database and return the list of lights
    # this sync function should be improved to only update the lights that have changed by filtering
    # the lights that have changed by comparing the light_id and the on status
    save_lights_task()
    lights = HueLight.objects.all()
    # Create context to pass to the template
    if not lights:
        context = {'error': 'Unable to retrieve light list.'}
    context = {'lights': lights}
    return render(request, 'philips_hue/light_list.html', context)


def get_light_detail(request, identifier):
    # light = get_object_or_404(HueLight, pk=pk)
    try:
        light = HueLight.objects.get(pk=identifier)
    except HueDevice.DoesNotExist:
        try:
            light = HueLight.objects.get(uuid=identifier)
        except HueLight.DoesNotExist:
            logger.error(f"Light with id or uuid '{identifier}' not found.")
            raise Http404("Light not found")
        except ValueError as e:
            logger.error(f"Invalid uuid format: {e}")
            raise Http404("Invalid identifier")

    return render(request, 'philips_hue/light_detail.html', {'light': light})


def update_light(request, pk):

    try:
        light = HueLight.objects.get(pk=pk)
        logger.warning(
            "I am calling the update_lights function in the view. lights_group is {}".format(light))
        logger.warning('the light {} status is {}.'.format(
            light.light_id, light.on))
        if light.on.on:
            light.set_light(light.light_id, 'on', False)
            logging.warning('the light {} is sucessfully turned Off.'.format(
                light.light_id, light.on))
        else:

            light.set_light(light.light_id, {'on': True, 'bri': 254})
            logging.warning('the light {} is sucessfully turned On.'.format(
                light.light_id, light.on))
            context = {"lights_group": light}
    except:
        raise Http404("There is no light info available.")
    return redirect('index', context)


def get_room_list(request):
    save_rooms_task()
    rooms = HueRoom.objects.all()
    # Create context to pass to the template
    if not rooms:
        context = {'error': 'Unable to retrieve room information in this hue.'}
    context = {'rooms': rooms}
    return render(request, 'philips_hue/room_list.html', context)

# identifier has to be the uid (aka, the `rid` of a device in the Hue API v2)
# endpoint could be one of ['light', 'device', 'room', 'grouped_light','scene', 'zone', 'entertainment', ]
# def get_endpoint_detail(endpoint,identifier):
#     endpoint_data = fetch_resource_endpoint_detail_task(endpoint=endpoint,identifier=identifier)
#     if endpoint_data:
#         endpoint_data = endpoint_data
#     else:
#         endpoint_data = []
#     return endpoint_data


def get_room_detail(request, pk):
    room = get_object_or_404(HueRoom, pk=pk)
    devices = room.children if room else []
    processed_grouped_lights = []

    if room and room.services:
        for service in room.services:
            if service['rtype'] == 'grouped_light':
                try:
                    grouped_lights = fetch_resource_endpoint_detail_task(
                        endpoint=service['rtype'], identifier=service['rid'])

                    for light in grouped_lights:
                        light_info = {
                            'rtype': light.get('type', 'Unknown'),
                            'rid': light.get('id', 'Unknown'),
                            # Convert to JavaScript boolean,
                            'on_status': 'true' if light.get('on', {}).get('on', False) else 'false',
                            'brightness': light.get('dimming', {}).get('brightness', 'Unknown'),
                            'brightness_delta': light.get('dimming_delta', 'Unknown'),
                            'signals': light.get('signaling', {}).get('signal_values', []),
                            'dynamics': light.get('dynamics', {}).get('signal_values', [])
                        }
                        processed_grouped_lights.append(light_info)
                except Exception as e:
                    logger.error(
                        f"Error getting lights for device {service['rid']}: {e}")

    context = {
        'room': room,
        'devices': devices,
        'grouped_lights': processed_grouped_lights,
    }
    return render(request, 'philips_hue/room_detail.html', context)


def get_device_list(request):
    save_devices_task()
    devices = HueDevice.objects.all()
    # Create context to pass to the template
    if not devices:
        context = {'error': 'Unable to retrieve room information in this hue.'}
    context = {'devices': devices}
    return render(request, 'philips_hue/device_list.html', context)


# this function use either pk or uuid of a device to get the device detail
def get_device_detail(request, identifier):
    lights = []
    try:
        device = HueDevice.objects.get(pk=identifier)
    except HueDevice.DoesNotExist:
        try:
            device = HueDevice.objects.get(uuid=identifier)
        except HueDevice.DoesNotExist:
            logger.error(f"Device with id or uuid '{identifier}' not found.")
            raise Http404("Device not found")
        except ValueError as e:
            logger.error(f"Invalid uuid format: {e}")
            raise Http404("Invalid identifier")
    if device:
        try:
            for service in device.services:

                if service['rtype'] and service['rtype'] == 'light':
                    # device.lights = HueLight.objects.filter(uuid__in=service['rid'])
                    lights.append({service['rtype']: service['rid']})
                # elif service['rtype'] and service['rtype'] == 'entertainment':
                #     device.entertainment = Group.objects.filter(uuid__in=service['rid'])
        except Exception as e:
            logger.error(f"Error getting lights for device {device.id}: {e}")
            # device.lights = []
    # return two additional context variables: lights and device.lights
    return render(request, 'philips_hue/device_detail.html', {'device': device, 'lights': lights})


def control_light_or_grouped_light(request, endpoint, identifier):
    if request.method == 'POST':
        data = json.loads(request.body)
        endpoint = data['endpoint']
        uuid = data['uuid']
        control_data = data['data']

        # Call your control_light_resource function
        response = control_light_resource(endpoint, uuid, control_data)

        return JsonResponse(response, safe=False)
    else:
        # current_light = fetch_resource_endpoint_detail_task(endpoint=endpoint,identifier=identifier)
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # {'endpoint': 'grouped_light', 'uuid': '01904780-2d89-4793-9...5656ad20d4', 'data': {'on': False, 'brightness': '100'}}
