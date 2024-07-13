from django.urls import path, include

from . import views

app_name = 'paymentapp'

urlpatterns = [
    path('handle/<int:order_id>', views.handle_stripe_payment, name='handle_stripe_payment'),
    path('success/', views.success, name='success'),
    path('failure/', views.failure, name='failure'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]