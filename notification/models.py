from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey


# Create your models here.
class Notification(models.Model):
    text = models.CharField(max_length=250)
    notification_type = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey("contenttypes.ContentType",on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey(
        "content_type", "object_id"
    )  # this dynammically findes the object


class ReadRecipt(models.Model):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="my_read_notifications"
    )
    at = models.DateTimeField(auto_now_add=True)
    notification = models.ForeignKey(
        "notification.Notification",
        on_delete=models.CASCADE,
        related_name="read_recipts",
    )
