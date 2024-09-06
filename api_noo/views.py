from django.shortcuts import render
from django.http.response import JsonResponse

# Create your views here.

def view1(request):
    print("call to api----------------------")
    print(request.headers)
    return JsonResponse({"I love":"Faati"})
    