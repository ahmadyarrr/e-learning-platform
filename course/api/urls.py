from .views import CourseViewSet, ModuleViewSet, SubjectViewset
from django.urls import include, path
from .views import Device, EnrollView, SubjectList,SubjectDetail,create_module
from rest_framework.routers import DefaultRouter
"""
    Routers automatically create urls for CRUD operations.
"""
app_name = 'courses'

routs_subject = DefaultRouter()
routs_subject.register('subjects',SubjectViewset)

routs_course = DefaultRouter()
routs_course.register('courses',CourseViewSet)

routs_module = DefaultRouter()
routs_module.register('modules',ModuleViewSet)

urlpatterns = [
    path('device',Device.as_view(),name="device"),
    
    path('subjects',SubjectList.as_view(),name="subjects_list"),
    path('<int:pk>/subject',SubjectDetail.as_view(),name='specific_subject'),
    path('module/create/',create_module,name="create_module"),

    # routers
    path('',include(routs_course.urls)),
    path('',include(routs_module.urls)),
    path('',include(routs_subject.urls))
]
