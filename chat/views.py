from typing import Any
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.http.response import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin

from course.models import Course
# Create your views here.

class AccessChatView(View,LoginRequiredMixin,TemplateResponseMixin):
    course = None
    template_name = 'chat/room.html'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        return context
    
    
    def get(self,request,course_id,*args, **kwargs):
        try:
            self.course =  request.user.enrolled_courses.get(id=course_id)
        except:
            return HttpResponseForbidden('Forbidden')
        
        return self.render_to_response({'course':self.course})
        