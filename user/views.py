import json

from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from modelapp.models import User


def hello_world(request: HttpRequest):
    return render(request, 'user/hello-world.html')


def nearby_restaurants(request: HttpRequest):
    return render(request, 'user/nearby-restaurants.html')


def restaurant(request: HttpRequest, restaurant_id: int):
    print(restaurant_id)

    return render(request, 'user/view-restaurant.html')


def review_order(request: HttpRequest, order_id: int):
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


class LoginView(View):

    def get(self, request: HttpRequest):
        logout(request)
        return render(request, 'user/login.html')

    def post(self, request: HttpRequest):

        email = request.POST.get('email')
        password = request.POST.get('password')

        print(email, password)

        user = authenticate(email=email, password=password)

        if user is None:
            return HttpResponse("Login failed")

        login(request, user)
        return redirect('landingapp:landing_page')






def register(request: HttpRequest):
    return render(request, 'user/register.html')

class RegisterView(View):
    def get(self, request: HttpRequest):
        return render(request, 'user/register.html')

    def post(self, request: HttpRequest):
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        try:
            user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
            login(request, user)
        except Exception as e:
            print(e)
            return render(request, 'user/register.html', {'error': str(e)})


        return redirect('landingapp:landing_page')


def edit_profile(request: HttpRequest):
    return render(request, 'user/edit-profile.html')


def rate(request: HttpRequest, order_id):
    return render(request, 'user/rate-rider-food.html')
