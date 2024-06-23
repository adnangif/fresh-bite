
from django.urls import path
from . import views


app_name = 'user'

urlpatterns = [
    path('hello-world/', views.hello_world),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),

    path('nearby/', views.nearby_restaurants, name='nearby_restaurants'),
    path('restaurants/<int:restaurant_id>/', views.restaurant, name='restaurant'),
    path('review-order/<int:order_id>/', views.review_order, name='review_order'),
    path('track-orders/', views.track_orders, name='track_orders'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('rate/<int:order_id>', views.rate, name='rate'),

    path('faq/', views.faq, name='faq'),
    path('feedback/', views.feedback, name='feedback'),
    path('live-chat/', views.livechat, name='livechat'),
]
