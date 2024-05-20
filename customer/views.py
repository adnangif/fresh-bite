from django.http import HttpRequest
from django.shortcuts import render


def hello_world(request: HttpRequest):
    return render(request, 'customer/hello-world.html')


def home(request: HttpRequest):
    return render(request, 'customer/home.html')

def nearby_restaurants(request: HttpRequest):
    return render(request, 'customer/nearby-restaurants.html')