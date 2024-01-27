
from django.shortcuts import render,redirect,get_object_or_404
#import the phue module to return the status of all lights
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
from philips_hue.tasks import fetch_resource_endpoint_task, save_lights_task, save_rooms_task,save_devices_task


logger = logging.getLogger('django.db')


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


def get_light_detail(request, pk):
    light = get_object_or_404(HueLight, pk=pk)
    return render(request, 'philips_hue/light_detail.html', {'light': light})


def update_light(request,pk):
    lights = HueLight.objects.get(pk=pk)
    logging.warning("I am calling the update_lights function in the view. lights_group is {}".format(lights))
    try:
        for light in lights:
            logging.warning('the light {} status is {}.'.format(light.light_id,light.on))
            if light.on:
                b.set_light(light.light_id,'on',False)
                logging.warning('the light {} is sucessfully turned Off.'.format(light.light_id,light.on))
            else:
                
                b.set_light(light.light_id,{'on':True,'bri':254})
                logging.warning('the light {} is sucessfully turned On.'.format(light.light_id,light.on))
        context ={"lights_group":lights}
    except :
        raise Http404("There is no light info available.")
    return redirect('index', context)

def get_room_list(request):
    save_rooms_task()
    rooms =  HueRoom.objects.all()
    # Create context to pass to the template
    if not rooms:
        context = {'error': 'Unable to retrieve room information in this hue.'}
    context = {'rooms': rooms}
    return render(request, 'philips_hue/room_list.html', context)


def get_room_detail(request, pk):
    room = get_object_or_404(HueRoom, pk=pk)
    return render(request, 'philips_hue/room_detail.html', {'room': room})


def get_device_list(request):
    save_devices_task()
    devices = HueDevice.objects.all()
    # Create context to pass to the template
    if not devices:
        context = {'error': 'Unable to retrieve room information in this hue.'}
    context = {'devices': devices}
    return render(request, 'philips_hue/device_list.html', context)


# def get_device_detail(request, pk):
#     device = get_object_or_404(HueDevice, pk=pk)
#     return render(request, 'philips_hue/device_detail.html', {'device': device})

def get_device_detail(request, identifier):
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
    
    return render(request, 'philips_hue/device_detail.html', {'device': device})