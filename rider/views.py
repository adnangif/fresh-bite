from django.http import HttpRequest, HttpResponse
from django.shortcuts import render



def login(request: HttpRequest) -> HttpResponse:

    return render(request, 'rider/login.html')


def register(request: HttpRequest) -> HttpResponse:
    return render(request, 'rider/register.html')


def edit_profile(request: HttpRequest) -> HttpResponse:
    return render(request,'rider/edit-profile.html')