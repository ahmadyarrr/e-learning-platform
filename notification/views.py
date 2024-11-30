from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from notification.models import Notification

# Create your views here.


@login_required
def mark_notification_read(request, id):
    try:
        notf_object = Notification.objects.get(id=id)
        notf_object.read_by.add(request.user)
        notf_object.save()
        return JsonResponse({"OK": "0"})
    except:
        return JsonResponse({"OK": "1"})
