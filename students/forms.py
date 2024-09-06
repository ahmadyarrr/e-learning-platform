from django import forms
from allauth.account.forms import SignupForm
from course.models import Course

class enroll_to_course_form(forms.Form):
    course = forms.ModelChoiceField(queryset=\
                                    Course.objects.all(),
                                    widget=forms.HiddenInput
                                    )

class StduentSignUpCustomForm(SignupForm):
    image = forms.ImageField()
    phone = forms.CharField(max_length=10)
    
    
    