from django.contrib.auth import login, authenticate
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from modelapp.models import Rider


# def login(request: HttpRequest) -> HttpResponse:
#
#     return render(request, 'rider/login.html')

class LoginView(View):
    def get(self, request):
        return render(request, 'rider/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        rider = authenticate(email=email, password=password)
        if rider and rider.role == 'rider':
            login(request, rider)

            return redirect('landingapp:landing_page')

        return render(request, 'rider/login.html', {'error': 'Invalid email or password.'})


class RegisterView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'rider/register.html')

    def post(self, request: HttpRequest) -> HttpResponse:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            rider = Rider.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password)
            login(request, rider)
            return redirect('landingapp:landing_page')
        except Exception as e:
            print(e)
            return render(request, 'rider/register.html', {'error': str(e)})


def edit_profile(request: HttpRequest) -> HttpResponse:
    return render(request,'rider/edit-profile.html')


def track_orders(request: HttpRequest) -> HttpResponse:
    return render(request, 'rider/track-orders.html')