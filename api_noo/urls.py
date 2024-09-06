from django.urls import path

from api_noo.views import view1

urlpatterns = [
    path("view1",view1,name="v1")
]
