from django.shortcuts import render
from django.forms import modelform_factory
from django.contrib.auth.models import User
from _account.forms import GenericDetailsForm
from instructors.forms import InstructorProfileForm
# Create your views here.


def personal_details(request):
    account_type = str(request.user.groups.first()).lower()
    if request.method == "POST":
        user_form = GenericDetailsForm(data=request.POST)
        if account_type == "instructors":
            profile_form = InstructorProfileForm(data=request.POST)
            
        elif account_type == "students":
            pass
        else:
            pass
    else:
        user_form = GenericDetailsForm(instance=request.user)
        if account_type == "instructors":
            profile_form = InstructorProfileForm(instance=request.user.instructor_profile)
        elif account_type == "students":
            pass
        else:
            pass
        
        return render(
            request,
            f"account/{account_type}/personal_detail.html",
            {
                "account_type": account_type,
                "user_form": user_form,
                "personal_form": profile_form,
            },
        )
