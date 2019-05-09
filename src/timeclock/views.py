from django.shortcuts import render

from django.views import View

# Create your views here.

from .models import UserActivity

class ActivityView(View):
    def get(self, request,*args, **kwargs):
        # current activity
        return render(request,"timeclock/activity-view.html",{})
    
    def post(self,request, *args,**kwargs):
        new_act=UserActivity.objects.create(user=request.user,activity='checkin')
        return render (request, "timeclock/activity-view.html",{})


# Django class based views
def activity_view(request,*args, **kwargs):
    if request.method=="POST":
        new_act=UserActivity.objects.crete(user=request.user,activity="checkin")
    return render (request,"timeclocks/activity-viwew.html")