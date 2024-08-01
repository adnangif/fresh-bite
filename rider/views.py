from django.contrib.auth import login, authenticate, logout
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from modelapp.models import Rider, Restaurant, Order, OrderedItem, OrderStatus, Transaction
from rider.decorators import rider_required
from rider.forms import UpdateRiderForm


class LoginView(View):
    def get(self, request):
        logout(request)

        return render(request, 'rider/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        rider = authenticate(email=email, password=password)
        if rider and rider.is_rider:
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
            rider = Rider.objects.create_user(first_name=first_name, last_name=last_name, email=email,
                                              password=password
                                              )
            return redirect('rider:login')
        except Exception as e:
            print(e)
            return render(request, 'rider/register.html', {'error': str(e)})


@atomic
@rider_required
def edit_profile(request: HttpRequest) -> HttpResponse:
    rider = Rider.objects.get(pk=request.user.id)
    location_object = rider.get_location_object()

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        is_available_for_ride = request.POST.get('is_available_for_ride')

        rider.first_name = first_name
        rider.last_name = last_name
        rider.email = email
        rider.phone = phone
        rider.is_available_for_ride = is_available_for_ride or False
        rider.save()

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location_in_string = request.POST.get('location')



        location_object.latitude = latitude if latitude else 31.5204
        location_object.longitude = longitude if longitude else 74.3587
        location_object.location_in_string = location_in_string or ''
        location_object.save()

    context = {
        'rider': rider,
    }
    return render(request, 'rider/edit-profile.html', context)


@rider_required
def track_orders(request: HttpRequest) -> HttpResponse:
    rider = Rider.objects.get(pk=request.user.id)
    orders: list[Order] = Order.objects.filter(rider=rider).order_by('-pk')
    order_list = []

    if request.method == 'POST':
        order_pk = request.POST.get('order_pk')
        order_status = request.POST.get('order_status')

        order = Order.objects.get(pk=order_pk, rider=rider)

        if order_status == OrderStatus.RIDER_ON_WAY:
            order.mark_as_rider_on_way()
        if order_status == OrderStatus.DELIVERED:
            order.mark_as_delivered()

    for order in orders:
        order_list.append({
            'order': order,
            'transaction': Transaction.objects.get(order=order),
            'restaurant': order.restaurant,
            'user': order.user,
            'items': OrderedItem.objects.filter(order=order),
        })

    context = {
        'order_list': order_list,
        'rider': rider,
        'empty_list': len(order_list) == 0,
        'order_status': OrderStatus,
    }
    return render(request, 'rider/track-orders.html', context)
