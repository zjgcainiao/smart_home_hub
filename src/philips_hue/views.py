
from django.shortcuts import render,redirect
from huesdk import Discover, Hue
# builds the response object
from django.http import HttpResponse
from django.http import Http404
from .models import MonitorLights
from decouple import config, Csv
from philips_hue.models import MonitorBridge
from django.utils import timezone
#import the phue module to return the status of all lights
# from huesdk import Discover
import os
import logging
from dotenv import load_dotenv

HUE_BRIDGE_IP_ADDRESS=os.getenv("HUE_BRIDGE_IP_ADDRESS")
HUE_BRIDGE_USERNAME=os.getenv("HUE_BRIDGE_USERNAME")
# Create your views here.

#connect to the Hue Bridge within the network
#this modules should be in the model.py??
# b=Bridge(HUE_BRIDGE_IP_ADDRESS,HUE_BRIDGE_USERNAME)

# https://discovery.meethue.com/ is the equivalent of the following code
# Discover the Hue Bridges
discover = Discover()
bridges = discover.find_hue_bridge_mdns(timeout=10)
# Iterate through the discovered bridges
for bridge_info in bridges:
    # Create a new MonitorBridge instance
    monitor_bridge = MonitorBridge(
        bridge_name=bridge_info["name"],
        bridge_ip_address=bridge_info["internalipaddress"],
        bridge_localtime=timezone.now(),  # Set current time for bridge_localtime
        bridge_timezone="Your_Timezone",  # Set your timezone or fetch it dynamically
        bridge_unique_id=bridge_info["id"]
    )
    
    # Save the instance to the database
    monitor_bridge.save()
# print(discover.find_hue_bridge_mdns(timeout=10))
# b.connect()
# lights=b.lights

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
    try:
        bright_status=MonitorLights.objects.all()
        # context = {'the light status': bright_status}
        context ={"lights_group":lights}

    except MonitorLights.DoesNotExist:
        raise Http404("There is no light info available.")
    return render(request, 'view.html', context)

def index_detail(request,light_id=3):
    return HttpResponse ("<h3>This is the detail page <p>light id: {}</p>.</h3>".format(light_id))

def update_lights(request):
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

  