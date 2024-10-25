from django import forms
from allauth.account.forms import SignupForm
from course.models import Course
from students.models import StudentProfile

class EnrollCourseForm(forms.Form):
    course = forms.ModelChoiceField(queryset=\
                                    Course.objects.all(),
                                    widget=forms.HiddenInput
                                    )

class StduentSignUpCustomForm(SignupForm):
    image = forms.ImageField()
    phone = forms.CharField(max_length=10)
    
    
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        exclude=['user',"image"]
    