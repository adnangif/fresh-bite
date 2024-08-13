import json
import random

from django.contrib.auth import login, authenticate, logout
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, resolve_url
from django.views import View

from chatbot_backend import generate_response
from modelapp.models import User, Restaurant, Menu, MenuItem, Cart, CartItem, PaymentTypes, Order, Rider, Transaction, \
    TransactionStatus, OrderedItem, OrderStatus, Review, ReviewTypes, ChatHistory, Message
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

    restaurants: list[Restaurant] = Restaurant.objects.raw(
        '''
        SELECT *
        FROM ((`modelapp_restaurant`
        INNER JOIN  `modelapp_person`  ON `modelapp_restaurant`.`owner_id`=`modelapp_person`.`id`)
        INNER JOIN `modelapp_location` ON  `modelapp_person`.`id`=`modelapp_location`.`entity_id`)
        WHERE `modelapp_restaurant`.`is_published`=1
        ORDER BY ((`latitude`-%s)*(`latitude`-%s)+(`longitude`-%s)*(`longitude`-%s))
        LIMIT 10
        ''', [latitude, latitude, longitude, longitude]
    )

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
        'restaurant_review_count': Review.objects.filter(
            review_type=ReviewTypes.RESTAURANT,
            order__restaurant=restaurant,
        ).count(),
        'food_reviews': Review.objects.filter(
            review_type=ReviewTypes.FOOD,
            order__restaurant=restaurant,
        ),
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

    # print(f"The Rider is: {Rider.objects.get_rider()}")

    if cart is None:
        return redirect('landingapp:landing_page')

    if request.method == 'POST' and cart_items_exist and user.okay_for_first_order():
        selected_rider = Rider.objects.get_rider()

        if not selected_rider:
            return HttpResponse("<h1>Rider Not Available. <a href='/'>Home</a></h1>")

        order = Order.objects.create_order(
            user=user,
            restaurant=cart.restaurant,
            rider=selected_rider,
        )
        print(order)
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
            order.send_email_to_user_notifying_of_order()
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


@user_required
def livechat(request: HttpRequest):
    user = User.objects.get(id=request.user.id)
    context = {
        'user': user,
        'chat_history': ChatHistory.objects.filter(user=user),
    }

    if request.method == 'POST':
        query = request.POST.get('query')
        reply = generate_response(query)

        current_message = ChatHistory.objects.create(
            user=user,
            query=query,
            reply=reply,
        )

        return render(request, 'user/livechat-message.html', {'chat': current_message})

    return render(request, 'user/live-chat.html', context)


@user_required
def livechat_with_rider(request: HttpRequest, order_id: int):
    order = Order.objects.get(id=order_id)
    if not order.is_rider_chat_open():
        return redirect('user:track_orders')

    sender = order.user
    receiver = order.rider

    context = {
        'order': order,
        'sender': sender,
        'receiver': receiver,
        'messages': Message.objects.filter(order_id=order_id),
    }

    if request.method == 'POST':
        message = Message.objects.create(
            order=order,
            sender=sender,
            receiver=receiver,
            text=request.POST.get('text'),
        )
        return HttpResponse(status=200)

    if request.method == 'GET' and request.GET.get('only-messages'):
        return render(request, 'user/rider-chat-all-messages.html', context)

    return render(request, 'user/live-chat-with-rider.html', context)


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
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        location_object.latitude = latitude if latitude else 31.5204
        location_object.longitude = longitude if longitude else 74.3587

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


@user_required
def restaurant_reviews(request: HttpRequest, restaurant_id: int):
    user: User = User.objects.get(pk=request.user.id)
    restaurant = Restaurant.objects.get(pk=restaurant_id)

    context = {
        "user": user,
        "restaurant": restaurant,
        "reviews": Review.objects.filter(
            review_type=ReviewTypes.RESTAURANT,
            order__restaurant=restaurant,
        )
    }

    return render(request, 'user/restaurant-reviews.html', context)


@user_required
def rider_reviews(request: HttpRequest, rider_id: int):
    rider = Rider.objects.get(pk=rider_id)

    context = {
        "rider": rider,
        "reviews": Review.objects.filter(
            review_type=ReviewTypes.RIDER,
            order__rider=rider,
        )
    }

    return render(request, 'user/rider-reviews.html', context)


@user_required
def upload_profile(request: HttpRequest):
    if request.method == "POST":
        img = request.FILES.get('image')
        user:User = User.objects.get(pk=request.user.id)

        user.profile_picture = img
        user.save()

    return redirect('user:edit_profile')
