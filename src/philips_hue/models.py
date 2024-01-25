from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, JSONField

LIGHT_STATUSES=[
    ('On','Light is On'),
    ('Off', 'Light is Off'),
]

BRIDGE_CHECK_CHOICE=[
    ('lights','Lights'),
    ('groups','Groups'),
    ('config','Config'),
]
class MonitorBridge(models.Model):
    id = models.AutoField(primary_key=True)

    bridge_name=models.CharField(max_length=20)
    bridge_ip_address=models.GenericIPAddressField()
    bridge_localtime=models.DateTimeField()
    bridge_timezone=models.CharField(max_length=20)
    bridge_unique_id=models.CharField(max_length=120,null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True)  # Maps to 'created_at'
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", null=True)  # Maps to 'updated_at'
    
    def __str__(self):
        return f"{self.bridge_name}_{self.bridge_ip_address}"
    class Meta:
        db_table = "MonitorBridge"
        ordering = ["-id"]
        verbose_name_plural="MonitorBridges"



class MonitorLights(models.Model):
    id = models.AutoField(primary_key=True)  # This represents the unique ID of the light in the database, not the Hue light ID
    light_name = models.CharField(max_length=120,null=True, blank=True)  # Maps to 'name'
    light_hue_id = models.CharField(max_length=120, null=True)  # Maps to 'id_', unique identifier of the Hue light
    light_is_on = models.BooleanField(default=False)  # Maps to 'is_on'
    light_bri = models.IntegerField(default=254, null=True, blank=True)  # Maps to 'bri'
    light_hue = models.IntegerField(null=True, blank=True)  # Maps to 'hue'
    light_sat = models.IntegerField(null=True, blank=True)  # Maps to 'sat'
    # light_product_id = models.CharField(max_length=120, null=True, blank=True)  # Specific to your application
    light_assigned_seq = models.CharField(max_length=3, null=True, blank=True)  # Specific to your application
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True)  # Maps to 'created_at'
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", null=True)  # Maps to 'updated_at'


    def __str__(self):
        return self.light_name  # Changed to return the name of the light

    class Meta:
        db_table = "MonitorLights"
        ordering = ["light_name"]
        verbose_name_plural = "MonitorLights"



class Group(models.Model):
    id= models.AutoField(primary_key=True)
    group_id = models.CharField(max_length=120, unique=True, verbose_name="Hue Group ID")  # Maps to 'id_'
    name = models.CharField(max_length=120, verbose_name="Group Name")  # Maps to 'name'
    is_on = models.BooleanField(default=False, verbose_name="Is On")  # Maps to 'is_on'
    brightness = models.IntegerField(default=254, verbose_name="Brightness")  # Maps to 'bri'
    hue = models.IntegerField(null=True, blank=True, verbose_name="Hue")  # Maps to 'hue'
    saturation = models.IntegerField(null=True, blank=True, verbose_name="Saturation")  # Maps to 'sat'
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True)  # Maps to 'created_at'
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", null=True)  # Maps to 'updated_at'

    def __str__(self):
        return self.name  # Return the group name for the string representation

    class Meta:
        db_table = "group"
        ordering = ["name"]
        verbose_name_plural = "Groups"

# class HueSchedule(models.Model):

## 2024-01-21 using Hue CLI API V2 and PostgreSQL database to store the data. here are the new data models:

# In this model:
# Fields that are less likely to change and are essential for identifying the light (like 'id' and 'owner') are stored as regular Django model fields.
# The JSONField is used for 'metadata', 'product_data', and 'state'. These fields can accommodate nested JSON objects.
class HueLight(models.Model):

    id = models.AutoField(primary_key=True)  # This represents the unique ID of the light in the database, not the Hue light ID
    uuid = models.UUIDField(null=True, blank=True)
    id_v1 = models.CharField(max_length=255)
    owner = JSONField(blank=True, null=True)
    metadata = JSONField(blank=True, null=True)  # Stores 'name', 'archetype', 'function'
    product_data = JSONField(blank=True, null=True)  # Stores product-specific data, {"function": "functional"}
    state = JSONField(blank=True, null=True)  # Stores 'on', 'dimming:{"brightness":100, "min_dim_level": 0.10000000149011612}, 'color_temperature', "diming_delta", "color_temperature_delta",'dynamics'
    type = models.CharField(max_length=255, blank=True, null=True)
    identify = models.JSONField(null=True, blank=True)
    alert = models.JSONField(null=True, blank=True)
    powerup = models.JSONField(null=True, blank=True)
    signaling = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", null=True)  # Maps to 'created_at'
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At", null=True)  # Maps to 'updated_at'

    def __str__(self):
        return self.metadata.get('name', 'Unknown Light')
    class Meta:
        db_table = "HueLight"
        ordering = ["id_v1"]
        verbose_name_plural = "HueLights"
    

class HueDevice(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(null=True, blank=True)
    id_v1 = models.CharField(max_length=255, blank=True, null=True)
    product_data = JSONField(blank=True, null=True)  # Stores the product data. model_id": "LCT024","manufacturer_name": "Signify Netherlands B.V.","product_name": "Hue play", "product_archetype": "hue_play", "certified": true,"software_version": "1.108.5", "hardware_platform_type": "100b-10e"
    metadata = JSONField(blank=True, null=True)  # Stores the metadata
    identify = JSONField(blank=True, null=True)  # Stores the identify data
    services = JSONField(blank=True, null=True)  # Stores the list of services
    type = models.CharField(max_length=100)  # e.g., "device"

    class Meta:
        db_table = "HueDevice"
        ordering = ["id_v1"]
        verbose_name_plural = "HueDevices"


class HueRoom(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(null=True, blank=True)
    id_v1 = models.CharField(max_length=255, unique=True,verbose_name="Hue Room ID (v1)")
    children = JSONField(blank=True, null=True)  # Stores the list of children devices
    services = JSONField(blank=True, null=True)  # Stores the list of services
    metadata = JSONField(blank=True, null=True)  # Includes name, archetype
    type = models.CharField(max_length=100,blank=True, null=True)  # e.g., "room"

    def __str__(self) -> str:
        name = self.metadata.get('name', 'Unknown Room')
        uuid = self.uuid
        id_v1 = self.id_v1
        return f'{name}_uuid_{uuid} ({id_v1})'

    class Meta:
        db_table = 'HueRoom'
        ordering = ["id_v1"]
        verbose_name_plural = "HueRooms"