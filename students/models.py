from django.db import models

# Create your models here.

class StudentProfile(models.Model):
    user = models.OneToOneField('auth.User',on_delete=models.CASCADE,related_name='student_profile')
    image = models.ImageField(upload_to='images/student',null=True,blank=True)
    phone  = models.CharField(max_length=10)
    