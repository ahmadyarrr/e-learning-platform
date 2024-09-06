import rest_framework.generics as rest_views

from course.api.perms import IsEnrolled
from .serializers import (
    CourseWithModuleContentSer,
    SimpleModuleSerializer,
    SubjectSerializer,
)
from course.models import Course, Module, Subject
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from user_agents import parse
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from .serializers import CourseSerializer
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.decorators import authentication_classes,permission_classes


class SubjectList(rest_views.ListAPIView):
    """
        this view retrives a group of subject objects
        but no longer used,instead the viewset is used
    """
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    throttle_classes = [AnonRateThrottle]


class SubjectDetail(rest_views.RetrieveAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class SubjectViewset(ModelViewSet):
    """
    A viewset for subject to handle CRUD
    """

    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    http_method_names = ["get","delete"]


class EnrollView(APIView):
    """
    a view to handle enrolling a student to a course
    this view is no more used. the logic is set in course viewset

    """

    authentication_classes = [BasicAuthentication]  # not needed since in settings
    permission_classes = [IsAuthenticated]  # not needed since in settings

    def post(self, request, pk, format=None):
        course = get_object_or_404(Course, id=pk)
        course.students.add(request.user)
        return Response({"Enrolled": True})

    def dispatch(self, request, *args, **kwargs):
        # your dispatch logic goes here
        return super().dispatch(request, *args, **kwargs)


class CourseViewSet(ModelViewSet):
    """
    A viewset handling CRUD and two other functionalities on a Course object
    1- enrolling a student          2- retriving the whole course with its contents

    note1: whatever new action we are adding to a viewset, the corresponding
            method name is generated after the main url pattern of the router
            e.g. contents() ---> api/courses/1/contents
            e.g. enrolli()  ---> api/courses/1/enrolli
    note2: if we have set default authentication classes set in settings,
            we don't need to override it for a custom action unless a new
            policy is needed for that action.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # custom functionality rather than CRUD
    @action(
        detail=True,
        methods=["post", "get"],
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated],
    )
    def enrolli(self, request, *args, **kwargs):
        course = self.get_object()  # works as retriving method
        course.students.add(self.request.user)
        return Response({"enrooled": True})

    @action(
        throttle_classes=[UserRateThrottle],
        detail=True,
        serializer_class=CourseWithModuleContentSer,
        permission_classes=[IsAuthenticated, IsEnrolled],
        methods=["get"],
        authentication_classes=[BasicAuthentication],
    )
    def contents(self, request, *args, **kwargs):
        """
        Retrives a course with its modules and contents.
        """
        return self.retrieve(request, *args, **kwargs)


class ModuleViewSet(ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = SimpleModuleSerializer


@api_view(["post"])
def create_module(request):
    """
        a FBVApi that could create a module using or simple serializer
    """
    data = request.data
    seri = SimpleModuleSerializer(data=data)

    if seri.is_valid():
        result = seri.save()
        return JsonResponse({"Created": "OK"}, status=201)
    return None


# just a test state
class Device(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.all()

    def get(self, request):
        print("Api called")
        data = request.META.get("HTTP_USER_AGENT", "wer")
        auth = request.META.get("HTTP_XAUTHORITY", None)
        print(request.META.get("AUTHORIZATION", None), "----sss")
        print(request.META)
        # print(auth)
        # device = parse(data)
        # print(device.browser,device.os.family,"-----------")
        return Response({"Enrolled": 1})
