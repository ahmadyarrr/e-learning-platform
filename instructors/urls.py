
from django.urls import path
from . import views
app_name = 'instructors'

urlpatterns = [
    path('register/',views.InstructorRegisterView.as_view(),name="register")
]
