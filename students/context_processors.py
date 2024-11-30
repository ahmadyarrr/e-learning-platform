from notification.models import Notification


def get_enrolled_courses(request):
    """
    this context manager is made to return an array of all courses the student is enrolled in
    """
    account_type = str(request.user.groups.first())
    prof = None
    if account_type == "Students":
        prof = request.user.student_profile
        return {
            "user_profile": prof,
            "enrolled_courses_ids": [
                course.id for course in request.user.enrolled_courses.all()
            ],
        }
    return {}


def get_notifications(request):
    notfs = []
    user = request.user
    if str(user) != "AnonymousUser":
        account_type = str(user.groups.first())
        if account_type == "Students":
            students_only = Notification.objects.filter(
                notification_type__in=["test", "assignment", "score"]
            )
            my_courses = [course.id for course in user.enrolled_courses.all()]
            for notf in students_only:
                if (
                    notf.related_object.course.id in my_courses
                    and not notf.read_by.contains(user)
                ):
                    notfs.append(notf)
        elif account_type == "Instructors":
            instructors_only = Notification.objects.filter(
                notification_type__in=["enrollment", "new_subject", "test_submission"]
            )
            for notf in instructors_only:
                if not notf.read_by.contains(user):
                    if notf.notification_type == "enrollment":
                        if notf.related_object.instructor == user:
                            notfs.append(notf)
                    elif notf.notification_type == "test_submission":
                        if notf.related_object.test.course.instructor == user:
                            notfs.append(notf)

        elif account_type == "Managers":
            pass

    return {
        "my_notifications": notfs,
        "amount_notifications": len(notfs),
    }
