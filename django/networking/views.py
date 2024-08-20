from django.shortcuts import render

# Create your views here.
# views.py in your Django app

from django.http import JsonResponse
from networking.utils import get_network_info  # Import your utility function

def get_network_info_view(request):
    network_data = get_network_info()
    return JsonResponse(network_data,safe=False)
