import json
from django.http import JsonResponse
from django.shortcuts import render
from allauth.account.views import SignupView
from django.views.generic.base import TemplateResponseMixin
from course.models import Course, Test, TestSection, TestCase, Option
from .models import InstructorProfile
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import InstructorRegisterForm
from django.contrib.auth.models import Group
from datetime import datetime
from pytz import timezone as py_timezone
from pytz import utc
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
                image=data["image"], phone=data["phone"], user=user,
                timezone= request.POST['timezone']
            )
            
            # adding user to a group
            instructors_group = Group.objects.get(name="Instructors")
            user.groups.add(instructors_group)
            # logging the user in
            login(request, user)
        else:
            return self.render_to_response({"form": form})
        return redirect("course:manage_course_view")


def create_test_view(request, course_id=None):
    """
        this view creates test, sections, testcases and option objects
        there are 3 steps:
            1- GET --> dialog for the instructor to insert test meta data
            2- POST--> receiving meta data and saving course and test section objects
            3- POST--> receiving questions and options
    """
    # handling POST requests
    if request.method == "POST":
        # if it is the test meta data
        body = json.loads(request.body)  # we should convert from binary to normal dict
        if "meta" in body:
            """this part is for creating test object and its sections"""
            try:
                # creating a test object
                instructor_tz = py_timezone(request.user.instructor_profile.timezone)
                course_id, duration = body["course_id"], body["duration"]

                start_date = instructor_tz.localize(datetime.fromisoformat(body["start_date"])).astimezone(utc)
                deadline= instructor_tz.localize(datetime.fromisoformat(body["deadline"])).astimezone(utc)
                print("start date from JS to utc", start_date)
                course = Course.objects.get(id=course_id)
                test = Test.objects.get_or_create(
                    course=course,
                    duration=duration,
                    date=start_date,
                    deadline=deadline,
                    active=False,
                )[
                    0
                ]  # (object, bool) when using get_or_create

                # creating the section objects
                sections = body["sections"]
                section_ids = []
                for sec in sections:
                    if sec != []:
                        amount_questions, sec_title, sec_type = (
                            sec[2][1],
                            sec[0][1],
                            sec[1][1],
                        )
                        test_section = TestSection.objects.create(
                            title=sec_title,
                            amount_questions=amount_questions,
                            question_type=sec_type,
                            test=test,
                        )
                        test_section.save()
                        section_ids.append(test_section.id)
                return JsonResponse({"response": 200,"section_ids":section_ids})
            except Exception as e:
                print("===",e   )
                return JsonResponse({"response": 500})
        elif "data" in body:
            """ 
                this part handles saving all question values and options
                data in JSON: [{sec_title:,type:, amount:, que_list: [{value,options:[], c_answer},{},{}]}, {nextSec}]
            """
            # print(" we are receiving questions ....")
            data = body["data"]  # array of questions
            for sec in data:
                # print("this is the section array --",sec)
                sec_title = sec["section_title"]
                sec_db_id = sec["section_id"]
                questions = sec["questions"]
                # print("this is the section id and questions array", sec_db_id, questions)
                section_obj = TestSection.objects.get(id=sec_db_id)
                # print("section object found ")
                # print("reading all related questions of this section")
                for index, q in enumerate(questions, 1):
                    # print("questoin",q,"index",index)
                    q_value = questions["q" + str(index)]["question"]
                    c_answer = questions["q" + str(index)]["c_ans"]
                    options = questions["q" + str(index)]["options"]
                    # print(q_value, c_answer, options)
                    test_case_ = TestCase.objects.create(
                        question=q_value, correct_answer=c_answer, section=section_obj
                    )
                    for index,opt in enumerate(options, 1):
                        Option.objects.create(
                            test_case=test_case_,
                            value=opt,
                            is_answer=bool(index == int(c_answer)),
                        )
            return JsonResponse({"OK":"yes"})
            # saviing questions and opotions

    # handling GET requests
    else:
        course = None
        try:
            course = Course.objects.get(id=course_id)
        except:
            pass
        return render(
            request, "courses/course/create_test.html", context={"course": course}
        )
