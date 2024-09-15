
def get_profile(request):
    account_type = str(request.user.groups.first())
    prof = None
    try:
        if account_type == "Students":
            prof  = request.user.student_profile
        elif account_type == "Managers":
            prof = request.user.manager_profile
        elif account_type == "Instructors":
            prof = request.user.instructor_profile
        else:
            pass
    except AttributeError:
        pass
    return {'user_profile':prof}