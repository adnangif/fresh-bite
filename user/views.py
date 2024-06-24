import json

from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from modelapp.models import User, Restaurant, Menu, MenuItem, Cart, CartItem
from user.decorators import user_required


def hello_world(request: HttpRequest):
    return render(request, 'user/hello-world.html')


def nearby_restaurants(request: HttpRequest):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    restaurants: list[Restaurant] = Restaurant.objects.all()

    context = {
        'restaurants': restaurants,
    }

    return render(request, 'user/nearby-restaurants.html', context)


@user_required
def restaurant(request: HttpRequest, restaurant_id: int):
    if request.method == 'POST':
        cart_pk = request.POST.get('cart_pk')
        item_pk = request.POST.get('item_pk')
        increment = request.POST.get('increment')
        decrement = request.POST.get('decrement')

        cart_item: CartItem = CartItem.objects.filter(cart=cart_pk, item=item_pk).last()
        if cart_item is None:
            CartItem.objects.create(cart_id=cart_pk, item_id=item_pk)
        elif increment:
            cart_item.increment()
        elif decrement:
            cart_item.decrement()

    menu_objects: list[Menu] = Menu.objects.filter(restaurant=restaurant_id)

    menu_list = []
    for menu_object in menu_objects:
        menu = {
            'name': menu_object.name,
            'pk': menu_object.pk,
            'items': [
                item for item in MenuItem.objects.filter(menu=menu_object)
            ],
        }
        menu_list.append(menu)

    cart = Cart.objects.get_or_create(restaurant=restaurant_id, user=request.user)[0]
    cart_items: list[CartItem] = CartItem.objects.filter(cart=cart)

    context = {
        'menu_list': menu_list,
        'restaurant': restaurant,
        'cart_items': cart_items,
        'cart': cart,
    }

    return render(request, 'user/view-restaurant.html', context)


@user_required
def review_order(request: HttpRequest, order_id: int):
    print(order_id)

    return render(request, 'user/review-order.html')


def livechat(request: HttpRequest):
    return render(request, 'user/live-chat.html')


@user_required
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
            return render(request, 'user/login.html', {"error": "Invalid email or password"})

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


@user_required
def edit_profile(request: HttpRequest):
    user: User = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')

        user.save()

    context = {
        'user': user,
    }

    return render(request, 'user/edit-profile.html', context)


@user_required
def rate(request: HttpRequest, order_id):
    return render(request, 'user/rate-rider-food.html')
