from django.contrib.auth import login, authenticate
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views import View

from modelapp.models import Owner


# Create your views here.


class LoginView(View):
    def get(self, request):
        return render(request, 'restaurant/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        owner = authenticate(email=email, password=password)

        if owner and owner.is_restaurant_owner():
            login(request, owner)
            return redirect('landingapp:landing_page')

        return render(request, 'restaurant/login.html', {'error': 'Invalid Credentials'})


class RegisterView(View):
    def get(self, request):
        return render(request, 'restaurant/register.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        try:
            owner = Owner.objects.create_user(email=email, password=password, first_name=first_name,
                                              last_name=last_name)

            login(request, owner)
            return redirect('landingapp:landing_page')

        except Exception as e:
            print(e)
            return render(request, 'restaurant/register.html', {'error': "Invalid"})


def edit_restaurant(request: HttpRequest):
    return render(request, 'restaurant/edit-restaurant.html')


def menus(request: HttpRequest):
    return render(request, 'restaurant/menu-list.html')


def add_menu(request: HttpRequest):
    return render(request, 'restaurant/add-menu.html')


def edit_menu(request: HttpRequest):
    return render(request, 'restaurant/edit-menu.html')


def track_orders(request: HttpRequest):
    return render(request, 'restaurant/track-orders.html')
