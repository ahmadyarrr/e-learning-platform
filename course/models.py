from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.urls import reverse
# Create your models here.

class Subject(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200,unique=True)
    owner = models.ForeignKey('auth.User',
                              on_delete=models.CASCADE,
                              related_name='subjects',
                              default=User.objects.get(username='sezar').id)
    description = models.TextField(null=True,blank=True)
    class Meta:
        ordering = [
            "title"
        ]
    
    def __str__(self) -> str:
        
        return "Subject {}.".format(self.title)
    
class Course(models.Model):
    instructor = models.ForeignKey("auth.User",
                                   on_delete=models.CASCADE,
                                   related_name="created_courses")
    
    subject = models.ForeignKey("Subject",
                                on_delete=models.CASCADE,
                                related_name="courses")
    students = models.ManyToManyField(User,
                                      related_name='enrolled_courses',
                                      blank=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200,
                            unique=True)

    created = models.DateTimeField(auto_now_add=True)
    overview = models.TextField()
    
    class Meta:
        ordering = ["-created"]
    
    def get_absolute_url(self):
        return reverse("course:detail_course", kwargs={"id": self.pk})
    
    
    def __str__(self) -> str:
        return "Course -{}- by -{}-".format(self.title,
                                             str(self.instructor))

class Module(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey("Course",
                               on_delete=models.CASCADE,
                               related_name="modules")
    description = models.TextField(blank=True)
    order = OrderField(for_fields=["course"],blank=True)
    class Meta:
        ordering = [
            "order"
        ]
    
    def __str__(self) -> str:
        return "{}-Module ({})  of course -{}-".format(str(self.order),
                                                            self.title,
                                                            str(self.course))
        
class Content(models.Model):
    module = models.ForeignKey("course.Module",
                               on_delete=models.CASCADE,
                               related_name="contents")
    order = OrderField(for_fields=["module"],blank=True)
    object_id = models.PositiveIntegerField()
    object_ct = models.ForeignKey("contenttypes.ContentType",
                                     on_delete=models.CASCADE,
                                     limit_choices_to={"model__in":(
                                         "image",
                                         "video",
                                         "text",
                                         "file"
                                         )}
                                )
    item = GenericForeignKey('object_ct',"object_id")
    
    class Meta:
        ordering=[
            'order'
        ]
    
    def __str__(self) -> str:
        return "{}-Content on module ({})".format(self.order,
                                                   str(self.module))
        
class BaseContent(models.Model):
    # this is not a model, but a class
    title = models.CharField(max_length=250)
    
    instructor = models.ForeignKey('auth.User',
                                   on_delete=models.CASCADE,
                                   related_name="%(class)s_related")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now = True)
    
    
    
    
    class Meta:
        ordering= ['created']
        abstract = True # a class that won't have any db table
        
    def __str__(self) -> str:
        return "Content: ".format()+self.title
    
    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html',
                                    {'item':self})
    
    
class Image(BaseContent):
    image = models.ImageField(upload_to="images")
    
class File(BaseContent):    
    file = models.FileField(upload_to="files")

class Video(BaseContent):
    url = models.URLField()
    
class Text(BaseContent):
    text = models.TextField()











