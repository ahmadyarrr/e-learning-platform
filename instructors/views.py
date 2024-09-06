from django.shortcuts import render
from allauth.account.views import SignupView
from django.views.generic.base import TemplateResponseMixin
from .models import InstructorProfile
from django.contrib.auth import login
from django.shortcuts import redirect
from .forms import InstructorRegisterForm
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
            # logging the user in
            login(request,user)
        else:
            return self.render_to_response({"form": form, "errors": form.errors})
        return redirect('course:manage_course_view')