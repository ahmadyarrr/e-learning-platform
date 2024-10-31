from django.http import HttpResponse
from django.shortcuts import render
from django.forms import modelform_factory
from django.contrib.auth.models import User
from _account.forms import GenericDetailsForm, ManagerProfileForm
from _account.models import ManagerProfile
from instructors.forms import InstructorProfileForm
from students.forms import StudentProfileForm
from students.models import StudentProfile

# Create your views here.


def personal_details(request):
    account_type = str(request.user.groups.first()).lower()
    """there is a harsh difference between data beign sent in get and post
        since we want this page to be rendered in either of those requests, we
        need to re caculate the forms after a post is doen to show the new info to
        the owner of the profile.
    """
    if request.method == "POST":
        user_form = GenericDetailsForm(instance=request.user, data=request.POST)
        if account_type == "instructors":
            profile_form = InstructorProfileForm(
                instance=request.user.instructor_profile, data=request.POST
            )
        elif account_type == "students":
            profile_form = StudentProfileForm(
                instance=request.user.student_profile, data=request.POST
            )
        elif account_type == "managers":
            profile_form = ManagerProfile(
                instance=request.user.manager_profile, data=request.POST
            )
        else:
            pass
        
        if user_form.is_valid() and profile_form.is_valid(): 
            user_form.save()
            profile_form.save()
            
    user_form = GenericDetailsForm(instance=request.user)
    try:
        if account_type == "instructors":
            profile_form = InstructorProfileForm(
                instance=request.user.instructor_profile
            )
        elif account_type == "students":
                profile_form = StudentProfileForm(
                    instance=request.user.student_profile
                )
        elif account_type == "managers":
            profile_form = ManagerProfileForm(
                instance=request.user.manager_profile
        )
        else:
            return HttpResponse("Not Found")
    except Exception:
        return HttpResponse("You have no profile")

    return render(
        request,
        f"account/{account_type}/personal_detail.html",
        {
            "account_type": account_type,
            "user_form": user_form,
            "personal_form": profile_form,
        },
    )
