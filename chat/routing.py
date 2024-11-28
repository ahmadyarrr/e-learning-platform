from django.urls import re_path
from chat import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/room/(?P<course_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/call/room/(?P<course_id>\d+)/$",consumers.CallConsumer2.as_asgi()),
]
