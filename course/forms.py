from django import forms
from django.forms.models import inlineformset_factory
from .models import Course,Module

ModuleForm = inlineformset_factory(
    Course,
    Module,
    fields=[
        "title",
        "description"
    ],
    extra=2,
    can_delete=True
)

TestForm = inlineformset_factory(
    Test,
    TestCase
)