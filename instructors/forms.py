from django import forms
from allauth.account.forms import SignupForm

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