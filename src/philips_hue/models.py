from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
# Create your models here.

LIGHT_STATUSES=[
    ('On','Light is On'),
    ('Off', 'Light is Off'),
]


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

    def __str__(self):
        return self.light_name  # Changed to return the name of the light

    class Meta:
        db_table = "MonitorLights"
        verbose_name_plural = "MonitorLights"

class MonitorBridge(models.Model):
    id = models.AutoField(primary_key=True)
    BRIDGE_CHECK_CHOICE=[
        ('lights','Lights'),
        ('groups','Groups'),
        ('config','Config'),
    ]
    bridge_name=models.CharField(max_length=20)
    bridge_ip_address=models.GenericIPAddressField()
    bridge_localtime=models.DateTimeField()
    bridge_timezone=models.CharField(max_length=20)
    bridge_unique_id=models.CharField(max_length=120,null=True)
    def __str__(self):
        return f"{self.bridge_name}_{self.bridge_ip_address}"
    class Meta:
        db_table = "MonitorBridge"
        verbose_name_plural="MonitorBridges"



class Group(models.Model):
    id= models.AutoField(primary_key=True)
    group_id = models.CharField(max_length=120, unique=True, verbose_name="Hue Group ID")  # Maps to 'id_'
    name = models.CharField(max_length=120, verbose_name="Group Name")  # Maps to 'name'
    is_on = models.BooleanField(default=False, verbose_name="Is On")  # Maps to 'is_on'
    brightness = models.IntegerField(default=254, verbose_name="Brightness")  # Maps to 'bri'
    hue = models.IntegerField(null=True, blank=True, verbose_name="Hue")  # Maps to 'hue'
    saturation = models.IntegerField(null=True, blank=True, verbose_name="Saturation")  # Maps to 'sat'

    def __str__(self):
        return self.name  # Return the group name for the string representation

    class Meta:
        db_table = "group"
        verbose_name_plural = "Groups"
