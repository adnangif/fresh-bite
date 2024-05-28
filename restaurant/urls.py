from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('edit-restaurant/', views.edit_restaurant, name='edit_restaurant'),

    path('menus/', views.menus, name='menus'),
]