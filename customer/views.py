from django.http import HttpRequest
from django.shortcuts import render


def hello_world(request: HttpRequest):
    return render(request, 'customer/hello-world.html')


def home(request: HttpRequest):
    return render(request, 'customer/home.html')

def nearby_restaurants(request: HttpRequest):
    return render(request, 'customer/nearby-restaurants.html')

def restaurant(request: HttpRequest, restaurant_id: int):
    print(restaurant_id)

    return render(request, 'customer/view-restaurant.html')
