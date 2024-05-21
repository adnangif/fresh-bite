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


def review_order( request: HttpRequest, order_id: int):
    print(order_id)

    return render(request, 'customer/review-order.html')


def livechat(request: HttpRequest):

    return render(request, 'customer/live-chat.html')


def track_orders(request: HttpRequest):

    return render(request, 'customer/track-orders.html')


def faq(request: HttpRequest):

    return render(request, 'customer/faq.html')


def feedback(request: HttpRequest):

    return render(request, 'customer/feedback.html')
