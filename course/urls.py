from django.urls import path
from . import views
from students import views as st_views
app_name = "course"

urlpatterns = [
    path("mine/", views.CourseManageView.as_view(), name="manage_course_view"),
    path("create/", views.CourseCreateView.as_view(), name="course_create"),
    path("<int:pk>/update", views.CourseUpdateView.as_view(), name="course_update"),
    path("<int:pk>/delete", views.CourseDeleteView.as_view(), name="course_delete"),
    path("<int:pk>/module", views.ModuleUpdateView.as_view(), name="module_manage"),
    path(
        "module/<int:module_id>/content/<model_name>/create",
        views.ContentCreateUpdateView.as_view(),
        name="module_content_create",
    ),
    path(
        "module/<int:module_id>/content/<model_name>/<int:id>",
        views.ContentCreateUpdateView.as_view(),
        name="module_content_update",
    ),
    path(
        "module/<int:id>",
        views.ModuleContentListInstructor.as_view(),
        name="module_content_list",
    ),
    path(
        '<int:course_id>/module/<pk>/lessons/',
        st_views.StudentModuleContentListView.as_view(),
        name='st_module_content_list'
    ),
    path(
        "<int:course_id>/module/<int:module_id>/lesson/<pk>",
        st_views.ContentDetail.as_view(),
        name='st_content_view'
    )
    ,
    path("content/<int:id>/delete",views.ContentDelete.as_view(), name="module_content_delete"),
    path("module/order/",views.ModuleOrder.as_view(),name="order_module"),
    path("content/order/",views.ModuleContentOrder.as_view(),name="order_content"),
    # details
    path('<slug:slug>/detail',views.PublicCourseDetail.as_view(),name="course_detail"),
    # search
    path("search/",views.search,name="search"),
]
