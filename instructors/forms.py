from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User

from instructors.models import InstructorProfile
class InstructorRegisterForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = {
            'username': self.fields['username'],
            'email': self.fields['email'],
            'password1': self.fields['password1'],
            'password2': self.fields['password2'],
            'image' : forms.ImageField(),
            'phone' : forms.CharField(max_length=10),
            'about' : forms.CharField(widget=forms.Textarea)
        }
        

class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        exclude=['user',"image"]