"""
URL configuration for educa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.views.decorators.cache import cache_page
from course.views import CourseDetail, SubjectCreateUpdateView, ViewCourses,SubjectManage

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/",include("allauth.urls")),
    path("course/",include("course.urls",namespace="course")),
    path("api/",include("course.api.urls",namespace='api')),
    # a course detail
    path("detail/<slug:slug>",CourseDetail.as_view(),name="course_detail"),
    # public courses
    path('',cache_page(5)(ViewCourses.as_view()),name="view_courses"),
    path('subject/<slug:subject>/',ViewCourses.as_view(),name='subject_courses'),
    # student
    path("student/",include('students.urls',namespace="students")),
    # instructors
    path("instructor/", include("instructors.urls"), name="instructors"),
    # subjects
    path("subjects/",SubjectManage.as_view(),name="manage_subjects"),
    path("subjects/create/",SubjectCreateUpdateView.as_view(),name="create_update_subject"),
    path('__debug__',include('debug_toolbar.urls')),
    # chat
    path('chat/',include('chat.urls',namespace="chat"))
]       

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
			  document_root= settings.MEDIA_ROOT)

