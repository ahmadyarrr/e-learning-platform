from django.urls import path
from .views import personal_details
app_name = "_account"
urlpatterns = [
    path("profile/personal_details",personal_details,name="show_profile")    
]
