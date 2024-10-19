from celery import shared_task

from course.models import Test


@shared_task
def mark_test_active(test_id):
    try:
        test = Test.objects.get(id=test_id)
        test.active= True
        test.save()
        print("test marked as active")
    except Exception as e:
        print(e.args, "priblew....")
        pass