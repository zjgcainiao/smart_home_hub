from django.contrib import admin

# Register your models here.
from .models import UserActivity

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["user","activity","timestamp"]
    list_filter =["timestamp"]
    class Meta:
        model = UserActivity

admin.site.register(UserActivity,UserActivityAdmin)


def __unicode__(self):
    return str(self.activity)

def __str__(self):
    return str(self.activity)