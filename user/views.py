import json
import random

from django.contrib.auth import login, authenticate, logout
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, resolve_url
from django.views import View

from modelapp.models import User, Restaurant, Menu, MenuItem, Cart, CartItem, PaymentTypes, Order, Rider, Transaction, \
    TransactionStatus, OrderedItem, OrderStatus, Review, ReviewTypes
from user.decorators import user_required
from user.forms import UpdateUserForm
import secrets


def hello_world(request: HttpRequest):
    return render(request, 'user/hello-world.html')


def nearby_restaurants(request: HttpRequest):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')

    print('latitude', latitude)
    print('longitude', longitude)

    restaurants: list[Restaurant] = Restaurant.objects.filter(is_published=True)

    context = {
        'restaurants': restaurants,
    }

    return render(request, 'user/nearby-restaurants.html', context)


@user_required
def view_restaurant(request: HttpRequest, restaurant_id: int):
    search_query: str = request.GET.get('q') or ''
    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == 'POST':
        cart_pk = request.POST.get('cart_pk')
        item_pk = request.POST.get('item_pk')
        increment = request.POST.get('increment')
        decrement = request.POST.get('decrement')
        cart = Cart.objects.get(pk=cart_pk)

        cart_item: CartItem = CartItem.objects.filter(cart=cart, item=item_pk).last()
        if cart_item is None:
            CartItem.objects.create(cart=cart, item_id=item_pk)
        elif increment:
            cart_item.increment()
        elif decrement:
            cart_item.decrement()

    menu_objects: list[Menu] = Menu.objects.filter(restaurant_id=restaurant_id)

    menu_list = []
    for menu_object in menu_objects:
        menu = {
            'name': menu_object.name,
            'pk': menu_object.pk,
            'items': [
                item for item in MenuItem.objects.filter(menu=menu_object,
                                                         name__icontains=search_query).order_by('-average_rating')
            ],

        }
        menu_list.append(menu)

    cart = Cart.objects.get_or_create(restaurant_id=restaurant_id, user=request.user)[0]
    cart_items: list[CartItem] = CartItem.objects.filter(cart=cart)

    context = {
        'menu_list': menu_list,
        'restaurant': restaurant,
        'cart_items': cart_items,
        'cart': cart,
    }

    return render(request, 'user/view-restaurant.html', context)


@user_required
@atomic
def review_order(request: HttpRequest, cart_id: int):
    cart: Cart = Cart.objects.filter(pk=cart_id, user=request.user.id).last()
    user = User.objects.get(id=request.user.id)
    cart_items: list[CartItem] = CartItem.objects.filter(cart=cart)
    cart_items_exist = CartItem.objects.filter(cart=cart).exists()

    if cart is None:
        return redirect('landingapp:landing_page')

    if request.method == 'POST' and cart_items_exist and user.okay_for_first_order():

        order = Order.objects.create_order(
            user=user,
            restaurant=cart.restaurant,
            rider=Rider.objects.all().last(),
        )
        transaction = Transaction.objects.create(
            order=order,
            payment_type=cart.payment_type,
            amount=cart.get_cart_total(),
            status=TransactionStatus.PENDING,
        )

        for item in cart_items:
            item.add_to_order(order=order)

        cart.delete()

        if transaction.payment_type == PaymentTypes.STRIPE:
            return redirect('paymentapp:handle_stripe_payment', order_id=order.id)
        else:
            return redirect('user:track_orders')

    cart_items: list[CartItem] = CartItem.objects.filter(cart=cart)

    context = {
        'cart_items': cart_items,
        'restaurant': cart.restaurant,
        'cart': cart,
        'user': user,
        'payment_types': PaymentTypes.choices,
        'next_url': resolve_url('user:review_order', cart_id=cart_id),
    }

    return render(request, 'user/review-order.html', context)


@user_required
def change_location(request: HttpRequest):
    user = User.objects.get(id=request.user.id)
    location_object = user.get_location_object()

    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location = request.POST.get('location')
        next_url = request.POST.get('next_url')

        location_object.latitude = latitude
        location_object.longitude = longitude
        location_object.location_in_string = location

        location_object.save()
        if next_url:
            return redirect(next_url)

    return HttpResponse("Not Allowed")


def livechat(request: HttpRequest):
    return render(request, 'user/live-chat.html')


@user_required
def track_orders(request: HttpRequest):
    orders: list[Order] = Order.objects.filter(user=request.user).order_by('-pk')
    order_list = []

    if request.method == 'POST':
        order_status = request.POST.get('order_status')
        order_pk = request.POST.get('order_pk')

        order = Order.objects.get(pk=order_pk, user=request.user)
        if order and order_status == OrderStatus.CANCELLED:
            order.mark_as_cancelled()

    for order in orders:
        order_list.append({
            'order': order,
            'transaction': Transaction.objects.get(order=order),
            'items': OrderedItem.objects.filter(order=order),
        })

    context = {
        'order_list': order_list,
        'order_status': OrderStatus,
    }
    return render(request, 'user/track-orders.html', context)


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

        if user and user.is_user:
            login(request, user)

            return redirect('landingapp:landing_page')

        return render(request, 'user/login.html', {"error": "Invalid email or password"})


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
            return redirect('user:login')
        except Exception as e:
            print(e)
            return render(request, 'user/register.html', {'error': str(e)})


@atomic
@user_required
def edit_profile(request: HttpRequest):
    user: User = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')

        location_object = user.get_location_object()

        location_object.latitude = request.POST.get('latitude')
        location_object.longitude = request.POST.get('longitude')
        location_object.location_in_string = request.POST.get('location')

        location_object.save()

        user.save()

    context = {
        'user': user,
    }

    return render(request, 'user/edit-profile.html', context)


@user_required
def rate(request: HttpRequest, order_id):
    order = Order.objects.get(pk=order_id)

    if request.method == 'POST':
        food_rating = request.POST.get('food_rating')
        food_review = request.POST.get('food_review')

        rider_rating = request.POST.get('rider_rating')
        rider_review = request.POST.get('rider_review')

        restaurant_rating = request.POST.get('restaurant_rating')
        restaurant_review = request.POST.get('restaurant_review')

        food = Review.objects.get_or_create(
            order=order,
            review_type=ReviewTypes.FOOD
        )[0]

        rider = Review.objects.get_or_create(
            order=order,
            review_type=ReviewTypes.RIDER,
        )[0]

        restaurant_review_obj = Review.objects.get_or_create(
            order=order,
            review_type=ReviewTypes.RESTAURANT
        )[0]

        if food_rating:
            try:
                order.rate_items(int(food_rating))
            except Exception as e:
                print("Food Rating Not Saved.")
                print(e)

        if restaurant_rating:
            try:
                order.view_restaurant.set_rating(int(restaurant_rating))
            except Exception as e:
                print("Restaurant Rating Not Saved.")
                print(e)

        food.rating = food_rating
        food.message = food_review
        food.review_type = ReviewTypes.FOOD
        food.save()

        rider.rating = rider_rating
        rider.message = rider_review
        rider.review_type = ReviewTypes.RIDER
        rider.save()

        restaurant_review_obj.rating = restaurant_rating
        restaurant_review_obj.message = restaurant_review
        restaurant_review_obj.review_type = ReviewTypes.RESTAURANT
        restaurant_review_obj.save()

        return redirect('user:track_orders')

    return render(request, 'user/rate-rider-food-restaurant.html')


@user_required
def change_personal_info(request: HttpRequest):
    user: User = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        next_destination = request.POST.get('next_destination')

        update_user_form = UpdateUserForm(request.POST, instance=user)
        if update_user_form.is_valid():
            update_user_form.save()

        return redirect(next_destination)

    else:
        return HttpResponse(status=400, content="Invalid method type")


@user_required
def change_cart_payment_type(request: HttpRequest):
    user: User = User.objects.get(pk=request.user.id)

    if request.method == 'POST':
        next_destination = request.POST.get('next_destination')
        cart_id = request.POST.get('cart_id')
        payment_type = request.POST.get('payment_type')

        cart = Cart.objects.get(pk=cart_id)
        cart.payment_type = payment_type
        cart.save()

        return redirect(next_destination)

    else:
        return HttpResponse(status=400, content="Invalid method type")
