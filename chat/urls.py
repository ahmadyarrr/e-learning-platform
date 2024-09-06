from django.urls import path
from . import views

app_name="chat"

urlpatterns = [
    path("room/<int:course_id>", views.AccessChatView.as_view(), name="course_chatroom")
]
