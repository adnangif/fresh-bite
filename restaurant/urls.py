from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('edit-restaurant/', views.edit_restaurant, name='edit_restaurant'),

    path('menus/', views.menus, name='menus'),
    path('add-menu/', views.add_menu, name='add_menu'),
    path('edit-menu/', views.edit_menu, name='edit_menu'),
    path('track-orders/', views.track_orders, name='track_orders'),
]