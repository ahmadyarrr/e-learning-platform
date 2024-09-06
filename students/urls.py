from django.urls import path
from . import views

app_name = "students"
urlpatterns = [
    path("register/", views.RegisterStudentView.as_view(), name="register"),
    path("courses/", views.StudentCourseList.as_view(), name="student_course_list"),
    path(
        "course/<pk>/",
        views.CourseDetail.as_view(),
        name="student_course_detail",
    ),
    path(
        "course/<pk>/<module_id>/",
        views.StudentCourseList.as_view(),
        name="student_course_detail_module",
    ),
]
