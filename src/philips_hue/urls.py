from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='lights'),
    url(r'^philips_hue/(\d+)/',views.index_detail,name='lights_detail'),
    url(r'ajax/update_lights/',views.update_lights,name='update_lights'),
]