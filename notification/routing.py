from django.urls import re_path
from notification.consumers import NotificationConsumer
"""
    re_path useage:
        it is used to enable the server to match complex urls
        () --> group capturing/saving which makes an arg accessible in the function
        (?p<something>) ---> creates keyword argument
        $ ---> shows the end of the expression/string
        [] --> groups a set of formula to add another forumula generally to them
        + ---> containes 1 or more charachters
        ^ ---> start of the string
        d+ --> one digit or more
        w+ --> alphabets, numbers, _
        [\w-]+ --> w+ and dash
         
"""
websocket_urlpatterns = [
    re_path(r"ws/notf/(?P<for>[\w-]+)/(?P<id>\d+)/$", NotificationConsumer.as_asgi()),
]
