from django.shortcuts import render
from allauth.account.views import SignupView
from django.views.generic.base import TemplateResponseMixin

from course.models import Test
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

def create_test_view(request):
    if request.method =='POST':
        # if it is the test meta data
        if 'meta' in request.POST:
            meta_data = request.POST['meta']
            course_id,duration,start_date, deadline = meta_data['course_id'],
            meta_data['duration'],
            meta_data['start_date'],
            meta_data['deadline']
            test = Test.objects.get_or_create(
                course= course_id,
                duration=duration,
                date =start_date,
                deadline=deadline,
                active=False
            )
            
            sections = meta_data['sections']
            for sec in sections:
                sec_title = sec['title']
                sec_type = sec['type']
                amount_questions = sec['amount']
            
            pass
        # full test creation
        else:
            pass
    else:
        return render(request,'courses/course/create_test.html')
    