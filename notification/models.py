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
    
    read_by = models.ManyToManyField(
        "auth.User",
        related_name="my_read_notifications"
    )
    
    class Meta:
        ordering = ['-created']


