from django.urls import path
from django.views.decorators.cache import cache_page
from .views import (
    courseEnrollView,
    ContentCreateUpdateView,
    ModuleContentOrder,
    ModuleOrder,
    ModuleUpdateView,
    CourseManageView,
    CourseCreateView,
    CourseDeleteView,
    CourseUpdateView,
    ModuleContentList,
    ContentDelete,
    CourseDetail,
    ViewCourses
)

app_name = "course"

urlpatterns = [
    path("mine/", CourseManageView.as_view(), name="manage_course_view"),
    path("create/", CourseCreateView.as_view(), name="course_create"),
    path("<int:pk>/update", CourseUpdateView.as_view(), name="course_update"),
    path("<int:pk>/delete", CourseDeleteView.as_view(), name="course_delete"),
    path("<int:pk>/module", ModuleUpdateView.as_view(), name="module_manage"),
    path(
        "module/<int:module_id>/content/<model_name>/create",
        ContentCreateUpdateView.as_view(),
        name="module_content_create",
    ),
    path(
        "module/<int:module_id>/content/<model_name>/<int:id>",
        ContentCreateUpdateView.as_view(),
        name="module_content_update",
    ),
    path(
        "module/<int:id>",
        ModuleContentList.as_view(),
        name="module_content_list",
    ),
    path("content/<int:id>/delete", ContentDelete.as_view(), name="module_content_delete"),
    path("module/order/",ModuleOrder.as_view(),name="order_module"),
    path("content/order/",ModuleContentOrder.as_view(),name="order_content"),
    path('enroll',courseEnrollView.as_view(),name="enroll_student"),
    # details
    
]
