from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Count
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import FormView
from django.views import View
from django.shortcuts import redirect
from django.apps import apps
from django.forms import modelform_factory
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from students.forms import enroll_to_course_form
from .forms import ModuleForm
from .models import Content, Course, Module, Subject
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse
from django.urls import reverse_lazy
from .mixins import (
    InstructorCourseMixin,
    InstructorCourseEditMixin,
    authenMixin,
)

from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.core.cache import cache

def slugify(sen):
    return "-".join(sen.split())


# Create your views here.


class SubjectManage(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "course.managers_access"
    model = Subject
    template_name = "subjects/list.html"
    context_object_name = "subjects"

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(owner=self.request.user)
        return qs


class SubjectCreateUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
    TemplateResponseMixin,
):
    permission_required = "course.managers_access"
    permission_denied_message = "only managers can change"
    obj = None
    model = Subject
    template_name = "subjects/create_update.html"


    def get_form(self, *args, **kwargs):
        form = modelform_factory(model=self.model, exclude=["owner", "slug"])
        return form(*args, **kwargs)

    def dispatch(self, request, id=None, *args, **kwargs):
        # print(type(super(self)),getattr(super(LoginRequiredMixin,self),'dispatch'),"-+_+_+_+_+_+_+_+")
        # print(type(super(View,self)),getattr(super(View,self),'dispatch'),"-+_+_+_+_+_+_+_+")
        # print(type(super(PermissionRequiredMixin,self)),getattr(super(PermissionRequiredMixin,self),'dispatch'),"-+_+_+_+_+_+_+_+")

        permission_response = super(PermissionRequiredMixin, self).dispatch(
            request, id, *args, **kwargs
        )
        if permission_response:
            if id:
                self.obj = get_object_or_404(self.model, id=id)
            return super().dispatch(request, id, *args, **kwargs)

    def get(self, request, id=None):
        subject_form = self.get_form(instance=self.obj)
        return self.render_to_response({"subject_form": subject_form, "obj": self.obj})

    def post(self, request, id=None):
        form = self.get_form(
            instance=self.obj, files=self.request.FILES, data=self.request.POST
        )
        if form.is_valid():
            # create new object
            instance = form.save(commit=False)
            instance.owner = self.request.user
            instance.slug = slugify(instance.title)
            instance.save()
            return redirect("manage_subjects")

        return self.render_to_response(
            {"subject_form": form, "errors": form.errors.as_ul, "obj": self.obj}
        )


class CourseDetail(DetailView):
    template_name = "courses/course/public_course_detail.html"
    model = Course
    context_object_name = "object"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["enroll_form"] = enroll_to_course_form(
            initial={"course": self.get_object}
        )
        return context


class CourseManageView(InstructorCourseMixin, ListView):
    permission_required = "course.view_course"
    permission_denied_message = "You are not allowed to see courses "
    template_name = "courses/manage/course/list.html"

    # model = Course
    # def get_queryset(self):
    #     all = super().get_queryset()
    #     # it should return
    #     return all.filter(instructor=self.request.user)


class CourseCreateView(InstructorCourseEditMixin, CreateView):
    permission_required = "course.add_course"


class CourseUpdateView(InstructorCourseEditMixin, UpdateView):
    permission_required = "course.change_course"


class CourseDeleteView(InstructorCourseMixin, DeleteView):
    template_name = "courses/manage/course/delete.html"
    permission_required = "course.delete_course"


# login required mixin does not work!
class ModuleUpdateView(LoginRequiredMixin,View, TemplateResponseMixin):
    template_name = "courses/manage/module/formset.html"
    course = None
    model = Module
    
    def get_formset(self, data=None):
        return ModuleForm(instance=self.course, data=data)

    def dispatch(self, request, pk=None, *args, **kwargs):
        self.course = get_object_or_404(Course, id=pk, instructor=request.user)
        return super().dispatch(request, pk, *args, **kwargs)

        
        
        
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({"course": self.course, "formset": formset})

    def post(self, requeset, *args, **kwargs):
        formset = self.get_formset(data=requeset.POST)
        if formset.is_valid():
            formset.save()
            return redirect("course:manage_course_view")
        # if form has erros
        return self.render_to_response({"course": self.course, "formset": formset})


# login required mixin does not work since we have defined dispatch!
class ContentCreateUpdateView(View, TemplateResponseMixin):
    module = None
    model = None
    obj = None  # for editing an existing instance, this is the starting point logic
    template_name = "courses/manage/content/form.html"

    # custom method
    def get_model(self, model_name):
        if model_name in ["video", "text", "file", "image"]:
            model = apps.get_model("course", model_name=model_name)
            return model
        return None

    # built or not ?? in method
    def get_form(self, model, *args, **kwargs):
        formm = modelform_factory(
            model=model, exclude=["instructor", "order", "created", "updated"]
        )

        return formm(
            *args, **kwargs
        )  # by calling this, all other args are passed. in post()

    # built in method
    def dispatch(self, request, module_id, model_name, id=None):
        # setting the model
        self.model = self.get_model(model_name)

        # setting module
        self.module = get_object_or_404(
            Module, id=module_id, course__instructor=request.user
        )

        # setting the object
        if id:
            self.obj = get_object_or_404(self.model, id=id, instructor=request.user)

        return super().dispatch(request, module_id, model_name, id)

    # built in method
    def get(self, request, module_id, model_name, id=None):
        # creating a form and passing it to the template
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response(
            {
                "form": form,
                "object": self.obj,
            }
        )

    # built in method
    def post(self, request, module_id, model_name, id=None):
        # validating the form and saving the object
        form = self.get_form(
            self.model, instance=self.obj, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            instance = form.save(
                commit=False
            )  # commit false since user is not specified and will cause error
            instance.instructor = request.user
            instance.save()
            if not id:
                # if a new obejct is being saved rather than an updating
                Content.objects.create(module=self.module, item=instance)
            return redirect("course:module_content_list", self.module.id)
        # if form is not valid , re-render the previous page with existing data
        return self.render_to_response({"form": form, "obejct": self.obj})


class ContentDelete(View):

    def post(self, request, id):
        content = get_object_or_404(
            Content, id=id, module__course__instructor=request.user
        )
        module = content.module
        content.item.delete()
        content.delete()
        return redirect("module_content_list", module.id)

    def get(self):
        # sending an error to client
        return JsonResponse({"Error": "Method not allowed"}, status=405)

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!----------------
    def put(self):
        from django.http import HttpResponseNotAllowed

        return HttpResponseNotAllowed(["Get", "Post"])

    def patch(self):
        return JsonResponse({"Error": "Method not allowed"}, status=405)

    def delete(self):
        return JsonResponse({"Error": "Method not allowed"}, status=405)


class ModuleContentList(TemplateResponseMixin, View):
    template_name = "courses/manage/module/content_list.html"

    def get(self, request, id):
        module = get_object_or_404(Module, id=id, course__instructor=request.user)
        return self.render_to_response({"module": module})


class ModuleOrder(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request, *args, **kwargs):
        dic = self.request_json
        for module_id, order in dic.items():
            Module.objects.filter(
                id=int(module_id), course__instructor=request.user
            ).update(order=order)
        return self.render_json_response({"saved": "OK"})


class ModuleContentOrder(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request, *args, **kwargs):
        dic = self.request_json
        for content_id, order in dic.items():
            # though we are aiming to retrieve only one object, but we use filter since get returns object not qs
            # we also could get and then do --- object.order = new_order_value
            Content.objects.filter(
                id=int(content_id), module__course__instructor=request.user
            ).update(order=order)

        return self.render_json_response({"saved": "OK"})


class ViewCourses(View, TemplateResponseMixin):

    template_name = "courses/course/public_list.html"

    def get(self, request, subject=None, *args, **kwargs):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.all().annotate(count_course=Count("courses"))
            cache.set('all_subjects',subjects)

        all_courses = Course.objects.annotate(amount_modules=Count('modules'))        
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            # creating a dynammic key for subject-specifc courses in cache
            key = f"subject_{subject.id}_courses"
            courses = cache.get(key)
            
            if not courses:
                # if courses not found in cache
                courses = Course.objects.filter(subject=subject)
                cache.set(key,courses)
        else:
            # if no subject is specified
            courses = cache.get('all_courses')
            if not courses:
                # if cache miss
                courses = all_courses
                cache.set('all_courses',all_courses)
                

        courses = Course.objects.all().annotate(count_module=Count("modules"))
        return self.render_to_response(
            {"courses": courses, "subjects": subjects, "subject": subject}
        )


class courseEnrollView(FormView, LoginRequiredMixin):
    course = None
    form_class = enroll_to_course_form

    def form_valid(self, form):
        # form valid always should return an httpResponse, the form is validated and data are available here
        self.course = form.cleaned_data["course"]
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        # this method is called by super().form_valid in return redirect HttpResponseRedirect(self.get_success_url)
        return reverse_lazy("student:student_course_detail", args=[self.course.id])
