
from django.shortcuts import render,redirect,get_object_or_404
#import the phue module to return the status of all lights
# from huesdk import Discover
from huesdk import Discover, Hue
# builds the response object
from django.http import HttpResponse
from django.http import Http404
from .models import MonitorLights
from decouple import config, Csv
from philips_hue.models import MonitorBridge
from django.utils import timezone
from django.db import transaction
import os
import logging
from dotenv import load_dotenv
import json  # Import the json module
import requests
from philips_hue.utilities import get_attributes,get_hue_connection,sync_lights_with_db

# light_name_list=[]
# light_id_list=[]
# light_on_list=[] # Boolean
# light_bri_list=[]
# for _ in b.lights:
#     light_name_list.append(_.name)
#     light_id_list.append(_.light_id)
#     light_on_list.append(_.on)
#     light_bri_list.append(_.brightness/254 if _.on else 0)


def index(request):

    hue = get_hue_connection()
    # print(discover.find_hue_bridge_mdns(timeout=10))
    if not hue:
        # Handle the error appropriately
        context = {'error': 'Unable to connect to Hue Bridge.'}
        return render(request, 'philips_hue/main.html', context)
    lights=hue.get_lights()
    context={'lights':lights}
    return render(request, 'philips_hue/main.html', context)



def get_light_list(request):
    # Sync Hue lights with the MonitorLights model
    lights = MonitorLights.objects.all()
    if not lights:
        lights = sync_lights_with_db()

    # Get the lights from the Hue bridge
    # lights = hue.get_lights()  # This is a placeholder, adjust based on how you fetch lights from your Hue connection

    # Create context to pass to the template
    context = {'lights': lights}
    return render(request, 'philips_hue/light_list.html', context)


def light_detail(request, pk):
    light = get_object_or_404(MonitorLights, pk=pk)
    return render(request, 'philips_hue/light_detail.html', {'light': light})

def update_light(request,pk):
    lights = MonitorLights.objects.get(pk=pk)
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

  