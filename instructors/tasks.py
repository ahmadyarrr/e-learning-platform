from celery import shared_task
from django.utils import timezone
from course.models import Test


@shared_task
def mark_test_active(test_id):
    try:
        test = Test.objects.get(id=test_id)
        test.active= True
        test.save()
        return True
    except Exception as e:
        return False

@shared_task
def mark_test_inactive(test_id):
    try:
        test = Test.objects.get(id=test_id)
        test.active = False
        test.save()
        return True    
    except:
        return False
