from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
# Create your models here.

LIGHT_STATUSES=[
    ('true','Light is On'),
    ('false' 'Light is Off'),
]

class MonitorLights(models.Model):
    id = models.AutoField(primary_key=True)
    light_name=models.CharField(max_length=120)
    light_product_id =models.CharField(max_length=120)
    light_mode=models.CharField(max_length=20)
    light_status=models.BooleanField(verbose_name="On/Off Status",default=True)
    light_bri=models.IntegerField(default=254)
    light_assigned_seq=models.CharField(max_length=3, null=True)
    
    def __str__(self):
        return f"self.light_status"
    class Meta:
        db_table = "MonitorLights"
        verbose_name_plural="MonitorLights"
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

