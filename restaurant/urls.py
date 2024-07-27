from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('edit-restaurant/', views.edit_restaurant, name='edit_restaurant'),

    path('menus/', views.menus, name='menus'),
    path('add-menu/', views.add_menu, name='add_menu'),
    path('edit-menu/<int:pk>', views.edit_menu, name='edit_menu'),
    path('delete-menu/', views.delete_menu, name='delete_menu'),
    path('track-orders/', views.track_orders, name='track_orders'),

    path('delete-item/', views.delete_item, name='delete_item'),

    path('change-restaurant-location/', views.change_restaurant_location, name='change_restaurant_location'),
    path('add-delivery-zone/', views.add_delivery_zone, name='add_delivery_zone'),
    path('remove-delivery-zone/', views.remove_delivery_zone, name='remove_delivery_zone'),
]