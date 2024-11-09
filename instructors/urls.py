
from django.urls import path
from . import views
app_name = 'instructors'

urlpatterns = [
    path('register/',views.InstructorRegisterView.as_view(),name="register"),
    path('create-test/<int:course_id>',views.create_test_view, name='create_test'),
    path("make-test/", views.create_test_view, name='make_test')


]
