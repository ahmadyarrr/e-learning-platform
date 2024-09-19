import django.forms as forms
from django.contrib.auth.models import User

from _account.models import ManagerProfile


class GenericDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "last_login",
            "date_joined",
        ]


class ManagerProfileForm(forms.ModelForm):
    class Meta:
        model = ManagerProfile
        exclude = ["image", "user"]
