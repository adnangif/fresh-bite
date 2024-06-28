import json

from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views import View

from modelapp.models import Owner, Restaurant, Menu, MenuItem, Order, OrderedItem
from restaurant.decorators import owner_required
from restaurant.forms import RestaurantForm, UpdateMenuItemForm


# Create your views here.


class LoginView(View):
    def get(self, request):
        logout(request)

        return render(request, 'restaurant/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        owner = authenticate(email=email, password=password)

        if owner and owner.is_restaurant_owner:
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


@owner_required
def edit_restaurant(request: HttpRequest):
    owner = Owner.objects.get(pk=request.user.id)
    restaurant: Restaurant = Restaurant.objects.get_or_create(owner=owner)[0]

    if request.method == 'POST':
        restaurant_form = RestaurantForm(request.POST, instance=restaurant)
        if restaurant_form.is_valid():
            restaurant_form.save()
            print("opens at ", restaurant.opens_at)

    context = {
        'name': restaurant.name,
        'opens_at': restaurant.opens_at.strftime('%H:%M:%S'),
        'closes_at': restaurant.closes_at.strftime('%H:%M:%S'),
        'phone': restaurant.phone,
        'phone2': restaurant.phone2,
    }

    return render(request, 'restaurant/edit-restaurant.html', context)


@owner_required
def menus(request: HttpRequest):
    restaurant = Restaurant.objects.get_or_create(owner__pk=request.user.id)[0]

    menu_objects: list[Menu] = Menu.objects.filter(restaurant=restaurant)

    menu_list = []

    for menu_object in menu_objects:
        menu = {
            'name': menu_object.name,
            'pk': menu_object.pk,
            'items': [
                item for item in MenuItem.objects.filter(menu=menu_object)
            ],
            'base': settings.MEDIA_URL
        }

        menu_list.append(menu)

    context = {
        'menu_list': menu_list,
    }

    return render(request, 'restaurant/menu-list.html', context)


@owner_required
def add_menu(request: HttpRequest):
    if request.method == 'POST':
        name = request.POST.get('name')
        restaurant = Restaurant.objects.get_or_create(owner__pk=request.user.id)[0]

        menu = Menu.objects.create(
            restaurant=restaurant,
            name=name
        )

        return redirect('restaurant:menus')

    return render(request, 'restaurant/add-menu.html')


@owner_required
def edit_menu(request: HttpRequest, pk: int):
    menu: Menu = Menu.objects.filter(pk=pk).last()

    if menu is None or menu.restaurant.owner.pk != request.user.pk:
        return redirect('restaurant:menus')

    if request.method == 'POST':
        item_pk = request.POST.get('item_pk')

        if item_pk:
            item = MenuItem.objects.get(pk=item_pk)
            menu_item_form = UpdateMenuItemForm(request.POST, request.FILES, instance=item)
            print(request.FILES)
            if menu_item_form.is_valid():
                menu_item_form.save()
            else:
                print(menu_item_form.errors)
        else:
            MenuItem.objects.create(
                menu_id=pk,
                description=request.POST.get('description'),
                name=request.POST.get('name'),
                price=request.POST.get('price'),
                image=request.FILES.get('image'),
            )

    context = {
        'name': menu.name,
        'menu_pk': menu.pk,
        'items': [
            item for item in MenuItem.objects.filter(menu=menu)
        ],

    }

    return render(request, 'restaurant/edit-menu.html', context)


@owner_required
def delete_menu(request: HttpRequest):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        menu: Menu = Menu.objects.get(pk=pk)

        if menu.restaurant.owner.pk == request.user.pk:
            menu.delete()

    return redirect('restaurant:menus')


@owner_required
def delete_item(request: HttpRequest):
    if request.method == 'POST':
        pk = request.POST.get('pk')
        item: MenuItem = MenuItem.objects.get(pk=pk)

        if item.menu.restaurant.owner.pk == request.user.pk:
            item.delete()

    return redirect('restaurant:menus')


@owner_required
def track_orders(request: HttpRequest):
    restaurant = Restaurant.objects.get_or_create(owner=request.user)[0]
    orders: list[Order] = Order.objects.filter(restaurant=restaurant).order_by('-pk')
    order_list = []

    for order in orders:
        order_list.append({
            'order': order,
            'items': OrderedItem.objects.filter(order=order),
        })

    context = {
        'order_list': order_list,
        'restaurant': restaurant,
    }

    return render(request, 'restaurant/track-orders.html', context)
