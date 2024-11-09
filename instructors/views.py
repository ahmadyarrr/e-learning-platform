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
from .tasks import mark_test_inactive
from datetime import timedelta


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
                image=data["image"],
                phone=data["phone"],
                user=user,
                timezone=request.POST["timezone"],
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
        2- POST--> saving test metadata, creating test sections and scheduling
        3- POST--> saving questions and options
    """
    # handling POST requests
    if request.method == "POST":
        body = json.loads(request.body)  # body of a fetch request is always converted
        if "meta" in body:
            """this part is for creating test object, sections and scheduling"""
            try:

                # creating the instructors timezone object
                instructor_tz = py_timezone(request.user.instructor_profile.timezone)
                course_id, duration = body["course_id"], body["duration"]
                title = body["test_title"]
                # creating a datetime with specific tz and converting to utc
                start_date = instructor_tz.localize(
                    datetime.fromisoformat(body["start_date"])
                ).astimezone(utc)
                # if we directly create the UTC, timing will not be exact (+xx:yy)
                deadline = instructor_tz.localize(
                    datetime.fromisoformat(body["deadline"])
                ).astimezone(utc)

                course = Course.objects.get(id=course_id)
                test = Test.objects.get_or_create(
                    title=title,
                    course=course,
                    duration=duration,
                    date=start_date,
                    deadline=deadline,
                )[
                    0
                ]  # (object, bool[true--> object created now]) when using get_or_create
                # telling celery to inactivate the test
                delay = (deadline - start_date).total_seconds()
                if delay > 1:
                    # mark_test_inactive.apply_async((test.id,),countdown=delay)
                    mark_test_inactive.apply_async((test.id,), eta=test.deadline)
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
                return JsonResponse({"response": 200, "section_ids": section_ids})
            except Exception as e:
                return JsonResponse({"response": 500})
        elif "data" in body:
            """
            this part handles saving all question values and options
            data in JSON: [{s_title:,s_id, type:, n_q:, q_list: [{value,options:[], c_answer},{},{}]}, {nextSec}]
            """
            # print(" we are receiving questions ....")
            data = body["data"]  # array of questions
            for sec in data:
                sec_title = sec["section_title"]
                sec_db_id = sec["section_id"]
                questions = sec["questions"]
                section_obj = TestSection.objects.get(id=sec_db_id)
                for index, q in enumerate(questions, 1):
                    question = questions["q" + str(index)]
                    q_value = question["question"] 
                    c_answer = question["c_ans"]
                    options = question["options"]
                    test_case_ = TestCase.objects.create(
                        question=q_value, correct_answer=c_answer, section=section_obj
                    )
                    for index, opt in enumerate(options, 1):
                        Option.objects.create(
                            test_case=test_case_,
                            value=opt,
                            is_answer=bool(index == int(c_answer)),
                        )
            return JsonResponse({"OK": "yes"})
    else:
        """
        Here, GET request is handled by following actions
        * sending a default start dateime and deadline in template
        * sending the course object
        """
        course = None
        tz = request.user.instructor_profile.timezone
        start_half_hour = (
            (datetime.now() + timedelta(hours=0.5))
            .astimezone(py_timezone(tz))
            .isoformat()
        )  #
        an_hour_later = timedelta(hours=1)
        defualt_deadline = (
            (an_hour_later + datetime.now())
            .astimezone(py_timezone(tz))
            .isoformat()
            .split(".")[0]
        )
        try:
            course = Course.objects.get(id=course_id)
        except:
            pass
        return render(
            request,
            "courses/course/create_test.html",
            context={
                "course": course,
                "default_start": start_half_hour.split(".")[0],
                "default_deadline": defualt_deadline,
            },
        )
