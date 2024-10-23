from celery import shared_task

from course.models import Test


@shared_task
def mark_test_active(test_id):
    try:
        test = Test.objects.get(id=test_id)
        test.active= True
        test.save()
    except Exception as e:
        pass

@shared_task
def mark_test_inactive(test_id):
    try:
        test = Test.objects.get(id=test_id)
        test.active = False
        test.save()
        
    except:
        pass
    
