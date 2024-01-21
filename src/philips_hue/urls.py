from django.urls import path
from django.urls import re_path

from philips_hue import views

app_name = 'philips_hue'

urlpatterns = [
    path('', views.index, name='dash'),
    path('lights/', views.get_light_list, name='light_list'),
    path('lights/<pk>', views.update_light, name='light_detail'),
    # path('lights/<pk>', views.udpate_light, name='update_light'),
    # re_path(r'^philips_hue/(\d+)/',views.index_detail,name='light_detail'),
    re_path(r'ajax/update_lights/',views.update_light,name='update_light'),
]