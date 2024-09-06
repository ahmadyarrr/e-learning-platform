from django.shortcuts import redirect
from .models import Course
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# 1 filtering by instructor
class InstructorMixin:
    def get_queryset(self):
        all = super().get_queryset()
        return all.filter(instructor=self.request.user)
    
# 2 adding instructor
class InstructorEditMixin:
    def form_valid(self,form):
        # combines the instructor
        form.instance.instructor = self.request.user
        return super().form_valid(form)
    
# 3 adding supplimentary course attributes 
class InstructorCourseMixin(InstructorMixin,
                            PermissionRequiredMixin,
                            LoginRequiredMixin):
    # supplies all remaining parts for a course
    model = Course
    fields = ["subject","title","slug","overview"]
    success_url = reverse_lazy("course:manage_course_view")
    
# 4 template supplier for create and update
class InstructorCourseEditMixin(InstructorCourseMixin,InstructorEditMixin):
    template_name=  "courses/manage/course/c_e_form.html"
    
class authenMixin:
    def __init__(self) -> None:
        print("---------------------------initialiezd------------------")
        if not self.request.user.is_authenticated():
            return redirect(reverse('account_login'))
        