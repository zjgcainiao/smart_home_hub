from django.urls import path
from django.urls import re_path

from philips_hue import views

app_name = 'philips_hue'

urlpatterns = [
    path('', views.index, name='dash'),
    path('lights/', views.get_light_list, name='light_list'),
    path('lights/<pk>', views.get_light_detail, name='light_detail'),
    # path('lights/<pk>', views.udpate_light, name='update_light'),
    # re_path(r'^philips_hue/(\d+)/',views.index_detail,name='light_detail'),
    re_path(r'ajax/update_lights/',views.update_light,name='update_light'),
    path('rooms/', views.get_room_list, name='room_list'),
    path('rooms/<pk>', views.get_room_detail, name='room_detail'),
    path('devices/', views.get_device_list, name='device_list'),
    path('devices/<pk>', views.get_device_detail, name='device_detail'),

]