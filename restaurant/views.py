from django.shortcuts import render

# Create your views here.


def login(request):
    return render(request, 'restaurant/login.html')


def register(request):
    return render(request, 'restaurant/register.html')