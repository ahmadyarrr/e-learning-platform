from django.urls import path
from . import views
from course import views as course_views

app_name = "students"
urlpatterns = [
    path("register/", views.RegisterStudentView.as_view(), name="register"),
    path("courses/", views.StudentCourseList.as_view(), name="student_course_list"),
    path(
        "course/<pk>/",
        views.StudentCourseDetail.as_view(),
        name="student_course_detail",
    ),
    path(
        "course/<pk>/module/<int:module_id>",
        views.StudentCourseDetail.as_view(),
        name="student_course_detail_module",
    ),
    path("addseen/", views.add_seen, name="addseen"),
    path("getseen/", views.list_seen, name="getseen"),
    path("join-exam/<int:pk>", views.join_exam, name="join_exam"),
    path("save/", views.save, name="save"),
]
