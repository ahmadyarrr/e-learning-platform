from unittest import TestCase
from django import forms
from django.forms.models import inlineformset_factory
from .models import Course,Module, Test, TestSection

def create_formset(kind, extra):
    if 'section' in kind:
        InlineTestSectionForm = inlineformset_factory(
        TestSection,
        TestCase,
        fields=[
            'question'
        ],
        extra=extra
    )
        return InlineTestSectionForm
        

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

