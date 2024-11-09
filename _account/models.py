from django.db import models

# Create your models here.

class ManagerProfile(models.Model):
    user = models.OneToOneField('auth.User',
                                on_delete=models.CASCADE,
                                related_name='manager_profile')
    image = models.ImageField(upload_to='images/manager',
                              null=True,
                              blank=True)
    phone  = models.CharField(max_length=10)
    about = models.TextField(null=True,blank=True)
    