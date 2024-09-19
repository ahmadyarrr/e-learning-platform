from django.urls import path
from . import views

app_name="chat"

urlpatterns = [
    path("room/<int:course_id>", views.AccessChatView.as_view(), name="course_chatroom"),
    path("conference_room/<int:course_id>",views.AccessCallView.as_view(),name="call_view")
]
