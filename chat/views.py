from typing import Any
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.http.response import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from .consumers import redis_client
from course.models import Course
import json
from django.http import JsonResponse

# Create your views here.


class AccessChatView(View, LoginRequiredMixin, TemplateResponseMixin):
    course = None
    template_name = "chat/room.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        return context

    def get(self, request, course_id, *args, **kwargs):
        try:
            self.course = request.user.enrolled_courses.get(id=course_id)
        except:
            return HttpResponseForbidden("Forbidden")

        return self.render_to_response({"course": self.course})


class AccessCallView(View, LoginRequiredMixin, TemplateResponseMixin):
    course = None
    template_name = "chat/call.html"

    def get(self, request, course_id, *args, **kwargs):
        try:
            self.course = request.user.enrolled_courses.get(id=course_id)
        except:
            return HttpResponseForbidden("Forbiden")

        return self.render_to_response({"course": self.course})


def send_new_messages(request):
    if request.method != 'POST' or not request.user.is_authenticated:
        return JsonResponse({'error':"ok"})
    body = json.loads(request.body)
    course_id = body.get("c_id",None)
    last_sent = body.get("m_id", 0)
    # taking out all course messages
    messages = json.loads(redis_client.get(f"mes_c{course_id}") or b"{}")
    # list for just sending messages
    sendings = []
    
    for i in range(last_sent, messages.__len__()):
        mess = messages[f"message_#{i}"]
        sendings.append({
            "id": i,
            "content": mess["message"],
            "sender_id": mess["sender_id"],
            "sender": request.user.username,
            "course": mess["cid"],
            "time": mess["time"],
        })
    # print("sending ",sendings)    
    return JsonResponse({"messages": json.dumps(sendings)})
