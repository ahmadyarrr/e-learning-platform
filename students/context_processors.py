def get_enrolled_courses(request):
    account_type = str(request.user.groups.first())
    prof = None
    try:
        if account_type == "Students":
            prof = request.user.student_profile
        elif account_type == "Managers":
            prof = request.user.manager_profile
        elif account_type == "Instructors":
            prof = request.user.instructor_profile
        else:
            pass
        return {
            "user_profile": prof,
            "enrolled_courses_ids": [
                course.id for course in request.user.enrolled_courses.all()
            ],
        }
    except AttributeError:
        pass
    return {}