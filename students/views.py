# from django.shortcuts import r/ender
from typing import Any
from django.db.models.query import QuerySet
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import authenticate, login
from course.models import Content, Course, Module
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from allauth.account.views import SignupView
from students.forms import StduentSignUpCustomForm
from students.models import StudentProfile
from django.views.generic.base import TemplateResponseMixin
from django.contrib.auth import login
from educa.settings import REDIS_DB_HOST,REDIS_DB_NAME, REDIS_DB_PORT
import redis, json
import pickle

# Create your views here.
redis_client = redis.Redis(host=REDIS_DB_HOST,
                           port=REDIS_DB_PORT,
                           db=REDIS_DB_NAME)


class RegisterStudentView(SignupView, TemplateResponseMixin):
    form_class = StduentSignUpCustomForm
    template_name = "account/students/register.html"
    
    
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return self.render_to_response({"form": form})
        
    def post(self, request, *args, **kwargs):
        form = StduentSignUpCustomForm(request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save(request)
            data = form.cleaned_data
            StudentProfile.objects.create(
                image=data["image"], phone=data["phone"], user=user
            )
            students_group = Group.objects.get(name="Students")
            user.groups.add(students_group)
            # logging the user in
            login(request,user)
        else:
            return self.render_to_response({"form": form})

        return redirect('students:student_course_list')


class StudentCourseList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    permission_required = ""
    model = Course
    template_name = "student/course/courses.html"
    context_object_name = "courses"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user.id
        courses_averages = {}
        for course in self.get_queryset():
            course_modules = course.modules.all()
            total = len(course_modules)
            m_seen_rates = {}
            for module in course_modules:
                key = f'm_{module.id}s_{user}'
                seen = redis_client.get(key)
                if seen:    
                    amount_seen = len(pickle.loads(seen))
                    m_seen_rate = amount_seen / total 
                    m_seen_rates[module.id] = m_seen_rate
            if total > 0:
                course_progress_average = sum([i for i in m_seen_rates.values()]) / total
                courses_averages[course.id] = course_progress_average
            else:
                courses_averages[course.id] = 0
        context['courses_averages'] = courses_averages
        return context 
    
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


class StudentCourseDetail(DetailView, LoginRequiredMixin):
    """
        provides students of a course with the materials avaialabe in the course
        and their progress in each module
    """
    template_name = "student/course/course_detail.html"
    model = Course

    def get_queryset(self):
        query = super().get_queryset()
        query.filter(students__in=[self.request.user])
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        # prerequisits for calculating progress
        total = course.modules.count()
        user = self.request.user.id
        # rates of seen modules      
        m_seen_rates = {}
        for module in course.modules.all():
            key = f'm_{module.id}s_{user}'
            seen = redis_client.get(key)
            if seen:    
                amount_seen = len(pickle.loads(seen))
                m_seen_rate = amount_seen / module.contents.count()  * 100
                m_seen_rates[module.id] = m_seen_rate
        context['modules_seen_rates'] = m_seen_rates # rates of seen of each module in template 
        context['course_progress_rate'] = sum([val for val in m_seen_rates.values()]) / total # the total progress of the course
        # setting the first module of the course 
        if "module_id" in self.kwargs:
            # set the specific module to template
            context["module"] = course.modules.get(id=self.kwargs["module_id"])
        else:
            # if not provided, set the last module of this course
            context["module"] = course.modules.all()[0]

        return context


class StudentModuleContentListView(DetailView,LoginRequiredMixin,PermissionRequiredMixin):
    """
        provides the students with a list of contents available in the module
        it also show's module-level progress of the student
    """
    template_name = 'courses/module/st_module_det.html'
    model = Module
    context_object_name = 'module'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        key = f'm_{self.get_object().id}s_{self.request.user.id}'
        redis_data = redis_client.get(key)
        context['percent_rate'] = 0
        if redis_data:
            amount = len(pickle.loads(redis_client.get(key)))
            total = self.get_object().contents.count()
            context['percent_rate'] = amount/total * 100
        
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        query = super().get_queryset()
        query = query.filter(course =self.kwargs['course_id'])
        return query


class ContentDetail(DetailView,LoginRequiredMixin,PermissionRequiredMixin):
    """
        provides the students with the content page
    """
    template_name = 'courses/content/ct_detail.html'
    model = Content
    context_object_name = 'content'
    
    def get_queryset(self) -> QuerySet[Any]:
        query = super().get_queryset()
        query = query.filter(module=self.kwargs['module_id'])
        return query
        

def add_seen(request):
    """
        this view adds the content id to redis with the specific key
        it just works on POST method.
    """
    if request.method == 'POST':
        request_data = json.loads(request.body)
        m_id, s_id,c_id  = request_data.get('m_id',None), request.user.id, request_data.get('c_id',None) # content id
        key = f'm_{m_id}s_{s_id}'
        
        # getting the raw bytestring from redis server 
        raw_data = redis_client.get(key)
        redis_data = []
        if raw_data:
            # converting raw bstring to the list which was saved
            redis_data = pickle.loads(raw_data) 
        if int(c_id) in redis_data:
            pass
        else:
            redis_data.append(int(c_id))
            redis_client.set(key,pickle.dumps(redis_data))
        return JsonResponse({'saved':True})
    
    return JsonResponse({'403':'method not allowed'})    


def list_seen(request):
    """
        this view returns a list of seen contents objects to client JS
    """
    request_data = json.loads(request.body)
    m_id, s_id, = request_data.get('m_id',None), request.user.id,
    key = f'm_{m_id}s_{s_id}'
    raw_data = redis_client.get(key)
    if raw_data:
        return JsonResponse({'seen':pickle.loads(raw_data)})
    else:
        return JsonResponse({'seen':False})