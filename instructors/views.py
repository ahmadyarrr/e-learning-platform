import json
from unittest import TestCase
from django.http import JsonResponse
from django.shortcuts import render
from allauth.account.views import SignupView
from django.views.generic.base import TemplateResponseMixin
from course.forms import create_formset
from course.models import Course, Test, TestSection
from .models import InstructorProfile
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import InstructorRegisterForm
from django.contrib.auth.models import Group

# Create your views here.
class InstructorRegisterView(SignupView, TemplateResponseMixin):
    form_class = InstructorRegisterForm
    template_name = "account/instructors/register.html"

    def get(self, request, *args, **kwargs):
        form = InstructorRegisterForm()
        return self.render_to_response({"form": form})

    def post(self, request, *args, **kwargs):
        form = InstructorRegisterForm(request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save(request)
            data = form.cleaned_data
            InstructorProfile.objects.create(
                image=data["image"], phone=data["phone"], user=user
            )
            # adding user to a group
            instructors_group = Group.objects.get(name="Instructors")
            user.groups.add(instructors_group)
            # logging the user in
            login(request, user)
        else:
            return self.render_to_response({"form": form})
        return redirect("course:manage_course_view")

def create_test_view(request,course_id=None):
    print(course_id,request.method)
    if request.method =='POST':
        # if it is the test meta data
        body = json.loads(request.body)
        if 'meta' in body:
            meta_data = body['meta']
            print("request came meta---",body)
            # creating a test object
            course_id,duration = body['course_id'],body['duration']
            start_date, deadline =  body['start_date'],body['deadline']
            print(start_date,deadline, "------dates")
            course = Course.objects.get(id=course_id)
            test = Test.objects.get_or_create(
                course= course,
                duration=duration,
                date =start_date,
                deadline=deadline,
                active=False
            )
            print("--------test instance created and saved")
            # getting sections data and preparing the appropriate forms
            json_answer = {'sections':[]}
            sections = body['sections']
            for sec in sections:
                sec_title , sec_type= sec['title'],sec['type']
                amount_questions = sec['amount']
                test_section = TestSection.objects.create(
                    title=sec_title,
                    amount_questions=amount_questions,
                    type_option=sec_type,
                    test= test
                )
                test_section.save()
                section_form = create_formset('section',amount_questions)
                # setting the section title and form to the list to be sent as json
                json_answer['sections'].append([sec_title,section_form])
            print('answer sent')
            return JsonResponse(json_answer)
        
        # full test creation
        else:
            pass
    # initial page
    else:
        course=None
        try:
            course = Course.objects.get(id=course_id)
        except:
            pass
        return render(request,
                      'courses/course/create_test.html',
                      context={'course':course})
    