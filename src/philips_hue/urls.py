from django.urls import path
from django.urls import re_path

from . import views

urlpatterns = [
    path('', views.index, name='lights'),
    re_path(r'^philips_hue/(\d+)/',views.index_detail,name='lights_detail'),
    re_path(r'ajax/update_lights/',views.update_lights,name='update_lights'),
]