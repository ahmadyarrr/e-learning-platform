from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.urls import reverse
from .utils import get_path
from django.utils.timezone import now

# Create your models here.


class Subject(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200)
    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="subjects",
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:

        return self.title


class Course(models.Model):
    instructor = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="created_courses"
    )

    subject = models.ForeignKey(
        "Subject", on_delete=models.CASCADE, related_name="courses"
    )
    students = models.ManyToManyField(User, related_name="enrolled_courses", blank=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    overview = models.TextField()
    image = models.ImageField(upload_to="course/covers")
    overview_video = models.FileField(
        upload_to="course/overview", null=True, blank=True
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["title",])
        ]

    def get_absolute_url(self):
        return reverse("course:detail_course", kwargs={"id": self.pk})

    def __str__(self) -> str:
        return "Course -{}- by -{}-".format(self.title, str(self.instructor))


class Module(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="modules"
    )
    description = models.TextField(blank=True)
    order = OrderField(for_fields=["course"], blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return "{}-Module ({})  of course -{}-".format(
            str(self.order), self.title, str(self.course)
        )


class Content(models.Model):
    module = models.ForeignKey(
        "course.Module", on_delete=models.CASCADE, related_name="contents"
    )
    order = OrderField(for_fields=["module"], blank=True)
    object_id = models.PositiveIntegerField()
    object_ct = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("image", "video", "text", "file")},
    )
    item = GenericForeignKey("object_ct", "object_id")

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return "{}-Content on module ({})".format(self.order, str(self.module))


class BaseContent(models.Model):
    # this is not a model, but a class
    title = models.CharField(max_length=250)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created"]
        abstract = True  # a class that won't have any db table

    def __str__(self) -> str:
        return "Content: ".format() + self.title

    def render(self):
        return render_to_string(
            f"courses/content/{self._meta.model_name}.html", {"item": self}
        )


class Image(BaseContent):
    image = models.ImageField(upload_to="images")


class File(BaseContent):
    file = models.FileField(upload_to="files")


class Video(BaseContent):
    url = models.URLField()


class Text(BaseContent):
    value = models.TextField()


# student productity
class Test(models.Model):
    title = models.CharField(max_length=60)
    course = models.ForeignKey('course.Course',
                               on_delete=models.CASCADE,
                               related_name='related_tests')
    date = models.DateTimeField(default=now)
    duration = models.PositiveSmallIntegerField(default=20) # in minutes
    deadline = models.DateTimeField(default=now)
    active = models.BooleanField(default=False)
    
    def get_absolute_url(self):
        return reverse("courses/test/test_detail.html", kwargs={"pk": self.pk})
    
    def __str__(self):
        return "Test "+self.title

class TestSection(models.Model):
    test = models.ForeignKey('course.Test',
                             on_delete=models.CASCADE,
                             related_name='sections')
    title = models.CharField(max_length=255)
    question_type = models.CharField(
        max_length=20,
        choices=[
            ("multiple","four-option",),
            ("true-false","True & False",),
            ("declarative","Declarative",),
        ],
    )
    amount_questions = models.PositiveSmallIntegerField() 

class TestCase(models.Model):
    section = models.ForeignKey('course.TestSection',
                                on_delete=models.CASCADE,
                                related_name='test_cases')
    
    correct_answer = models.PositiveSmallIntegerField(null=True, blank=True)
    question = models.TextField()
    def __str__(self):
        return self.question


class Option(models.Model):    
    test_case = models.ForeignKey('course.TestCase',
                                  on_delete=models.CASCADE,
                                  related_name='options')
    value = models.CharField(max_length=20)
    is_answer = models.BooleanField(default=False)


class Score(models.Model):
    student  = models.ForeignKey('auth.User',
                                 on_delete=models.CASCADE,
                                 related_name='st_scores')
    
    hw = models.ForeignKey('course.Assignment',
                            on_delete=models.CASCADE,
                            related_name='related_scores',
                            null=True,
                            blank=True
                                 )
    
    test = models.ForeignKey('course.Test',
                             on_delete=models.CASCADE,
                             related_name='related_scores',
                             null=True,
                             blank=True)
    course = models.ForeignKey('course.Course',
                               on_delete=models.CASCADE,
                               related_name='related_scores')
    
    value = models.FloatField(default=0)

class Assignment(models.Model):
    student  = models.ForeignKey('auth.User',
                                 on_delete=models.CASCADE,
                                 related_name='related_hws')
    
    course = models.ForeignKey('course.Course',
                               on_delete=models.CASCADE,
                               related_name='related_hws')
    document = models.FileField(upload_to= get_path)
    start = models.DateTimeField(default=now)
    deadline = models.DateTimeField(default=now)

# will be applied later, it is an action bar
# class Notification(models.Model):
#     course = models.ForeignKey('course.Course',
#                                 on_delete=models.CASCADE,
#                                 related_name='notifications')
#     active = models.BooleanField(default=True)
#     to = models.CharField(max_length=10,hoices=('instructor','student'))
