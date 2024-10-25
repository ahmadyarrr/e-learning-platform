from django.db.models.signals import post_save
from django.dispatch import receiver
from course.models import Test
from django.utils import timezone
from .tasks import mark_test_active

@receiver(post_save,sender=Test)
def schedule_test(sender,instance,created,**kwargs):
    """this signal function schedules a test object to be marked as active"""
    test = instance
    if not test.active:
        test_start_date = test.date 
        delay = (test_start_date - timezone.now()).total_seconds()
        if delay > 0:
            mark_test_active.apply_async((test.id,), countdown=delay)
        else:
            pass
