from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.


def login(request):
    return render(request, 'restaurant/login.html')


def register(request):
    return render(request, 'restaurant/register.html')

def edit_restaurant(request: HttpRequest):
    return render(request,'restaurant/edit-restaurant.html')


def menus(request: HttpRequest):
    return render(request, 'restaurant/menu-list.html')