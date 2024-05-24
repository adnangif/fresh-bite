from django.http import HttpRequest
from django.shortcuts import render


def hello_world(request: HttpRequest):
    return render(request, 'user/hello-world.html')

def nearby_restaurants(request: HttpRequest):
    return render(request, 'user/nearby-restaurants.html')

def restaurant(request: HttpRequest, restaurant_id: int):
    print(restaurant_id)

    return render(request, 'user/view-restaurant.html')


def review_order( request: HttpRequest, order_id: int):
    print(order_id)

    return render(request, 'user/review-order.html')


def livechat(request: HttpRequest):

    return render(request, 'user/live-chat.html')


def track_orders(request: HttpRequest):

    return render(request, 'user/track-orders.html')


def faq(request: HttpRequest):

    return render(request, 'user/faq.html')


def feedback(request: HttpRequest):

    return render(request, 'user/feedback.html')


def login(request: HttpRequest):
    return render(request, 'user/login.html')


def register(request: HttpRequest):
    return render(request, 'user/register.html')
