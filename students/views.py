# from django.shortcuts import r/ender
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from course.models import Course
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from allauth.account.views import SignupView
from students.forms import StduentSignUpCustomForm
from students.models import StudentProfile
from django.views.generic.base import TemplateResponseMixin
from django.contrib.auth import login
# Create your views here.


class RegisterStudentView(SignupView, TemplateResponseMixin):
    form_class = StduentSignUpCustomForm
    template_name = "account/students/register.html"
    
    def get(self, request, *args, **kwargs):
        form = StduentSignUpCustomForm()
        return self.render_to_response({"form": form})

    def post(self, request, *args, **kwargs):
        form = StduentSignUpCustomForm(request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save(request)
            data = form.cleaned_data
            StudentProfile.objects.create(
                image=data["image"], phone=data["phone"], user=user
            )
            print('ok')
            # logging the user in
            login(request,user)
        else:
            return self.render_to_response({"form": form, "errors": form.errors})
        return redirect('students:student_course_list')


# class Register_student(CreateView):

#     template_name = "account/register_student.html"
#     form_class = UserCreationForm
#     success_url = reverse_lazy("student:student_course_list")

#     def form_valid(self, form):
#         # form valid method should always return a httpResponse
#         result = super().form_valid(form)
#         user_name = form.cleaned_data["username"]
#         password = form.cleaned_data["password1"]
#         user = authenticate(username=user_name, password=password)
#         login(self.request, user)
#         print("this is the result of super valid form---->", result)
#         return result


class StudentCourseList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    permission_required = ""
    model = Course
    template_name = "student/course/courses.html"
    context_object_name = "courses"

    def get_queryset(self):
        query = super().get_queryset()
        # save the return value, not just by calling filter it affects
        query = query.filter(students__in=[self.request.user])
        return query

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            instructor = Group.objects.get(name="Instructors")
            managers = Group.objects.get(name="Managers")
            # redirect to manage courses page for teachers
            if instructor in self.request.user.groups.all():
                return redirect("course:manage_course_view")
            # redirect to manage subjects page for managers
            elif managers in self.request.user.groups.all():
                return redirect("manage_subjects")
        # redirect to default url
        return super().dispatch(*args, **kwargs)


class CourseDetail(DetailView, LoginRequiredMixin):
    template_name = "student/course/detail.html"
    model = Course

    def get_queryset(self):
        query = super().get_queryset()
        query.filter(students__in=[self.request.user])
        return query

    def get_context_data(self, **kwargs):
        # we override it so that send the module to template too
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        if "module_id" in self.kwargs:
            # set the specific module to template
            context["module"] = course.modules.get(id=self.kwargs["module_id"])
        else:
            # if not provided, set the last module of this course
            context["module"] = course.modules.all()[0]

        return context
