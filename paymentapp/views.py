import json

import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from modelapp.models import Order
from user.decorators import user_required


@user_required
def handle_stripe_payment(request, order_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order = Order.objects.get(id=order_id)
    ordered_items = order.get_ordered_items()

    order.handle_stripe_dependency()
    line_items = [
        {
            'price': item.item.stripe_price,
            'quantity': item.quantity,
        } for item in ordered_items
    ]

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=settings.SERVER_DOMAIN + "payment/success",
            cancel_url=settings.SERVER_DOMAIN + "payment/failure",
        )

        print("------------checkout session------------")
        print(checkout_session)
        print('------------checkout session------------')
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url)


def success(request):
    return HttpResponse('Successful!')


def failure(request):
    return HttpResponse('Failed!')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print('Error parsing payload: {}'.format(str(e)))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Error verifying webhook signature: {}'.format(str(e)))
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        print(json.dumps(payment_intent, indent=4))
        print('PaymentIntent was successful!')
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object  # contains a stripe.PaymentMethod
        print('PaymentMethod was attached to a Customer!')
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
