from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django.utils import timezone
# Create your models here.
# class UserDaytimes(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL)
#     today =models.DateField()

USER_ACTIVITY_CHOICES= (
    ('checkin', "Check In"),
    ('checkout',"Check Out")
)

class UserActivity(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    activity =models.CharField(max_length =120, default ="checkin",choices = USER_ACTIVITY_CHOICES)
    timestamp=models.DateTimeField(auto_now_add=True)
# daily time clock

def __unicode__(self):
    return str(self.activity)

def __str__(self):
    return str(self.activity)

class Meta:
    verbose_name = "Activity"
    verbose_name_plural = "User Activities"