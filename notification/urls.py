from django.urls import path
from .views import mark_notification_read

app_name = 'notification'
urlpatterns = [
    path('mark-read/<int:id>',mark_notification_read,name="mark-notf-read")
]

