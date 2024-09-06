from rest_framework import serializers
from django.contrib.auth.models import User
from course.models import Content, Course, Module, Subject

"""
    Qustions:
        1- how to create a foreignKey relation both sides in a many-side's serializer?
            e.g. createing a course with its modules in a module serializer
        2- How to control a foreignKey field realtion as a serailizer.
        
"""


class SubjectSerializer(serializers.ModelSerializer):
    # a  serializer that helps in creating, retriving a subject
    class Meta:
        model = Subject
        fields = ["id", "title", "slug"]


class SimpleModuleSerializer(serializers.Serializer):
    """
    a module serializer that could serilzie one or many modules
    this is a simple serializer rather than a model serializer, every method is
    overriden; But just create has to be overriden since it is not implemented.

    There is a problem with related objects. The side being foreignKey-ed could not be created
    or updated in a many-side serializer.
    """

    # course = CourseSerializer()
    course = serializers.IntegerField()
    order = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()

    def is_valid(self, raise_exception=True):
        """this method is called initially
        we pass raise_exception=True so that it raise exceptions
        """
        return super().is_valid(raise_exception=True)

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        """this method either creates or updates a module"""
        course = Course.objects.get(id=validated_data.pop("course"))
        module = Module.objects.get_or_create(course=course, **validated_data)
        return module


class CourseSerializer(serializers.ModelSerializer):
    """
    a course serializer that is used for creating, updating and retriving
    a course object or many.we have customized modules field since it
    could have its own serializer an it is a related object.
    """

    modules = SimpleModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["title", "slug", "overview", "subject", "instructor"]

    def is_valid(self, raise_exception=True):
        return super().is_valid(raise_exception=True)

    def validate(self, attrs):
        return super().validate(attrs)


class ItemField(serializers.RelatedField):
    """
    An auto serializing field
    used in content serializer to serialize the item of the contenttype
    """

    def to_representation(self, content):
        return content.render()


class ContentSerializer(serializers.ModelSerializer):
    """
        A nested serializer that contains two other serializers inside it,
        Item serailizer and Module serializer.
        used in module serializer as a field to represent contents of the module
    """

    item = ItemField(read_only=True)
    module = SimpleModuleSerializer

    class Meta:
        model = Content
        fields = ["module", "order", "item"]


class ModuleWithContentSer(serializers.ModelSerializer):
    """
    A nested serializer for Module with its content serializer.
    Used in course-with-modude-content-serializer as a field
    to represent many moduels with their content
    """

    contents = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ["title", "order", "description", "contents"]


class CourseWithModuleContentSer(serializers.ModelSerializer):
    """
    A serializer that serializes a course with all its modules and contents
    """

    modules = ModuleWithContentSer(many=True)

    class Meta:
        model = Course
        fields = [
            "title",
            "overview",
            "instructor",
            "subject",
            "created",
            "modules",
            "slug",
            "id",
        ]
