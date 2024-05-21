
from django.urls import path
from . import views
urlpatterns = [
    path('hello-world/', views.hello_world),
    path('home/', views.home),
    path('nearby/', views.nearby_restaurants),
    path('restaurants/<int:restaurant_id>/', views.restaurant),
    path('review-order/<int:order_id>/', views.review_order),
]
