from django.urls import path
from django.urls import re_path

from networking.views import get_network_info_view

app_name = 'netowrking'

urlpatterns = [
    path('basic/', get_network_info_view, name='basic_network_info'),

]