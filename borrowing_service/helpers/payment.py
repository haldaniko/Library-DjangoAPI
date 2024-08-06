import stripe
from django.urls import reverse
from django.http import HttpRequest
from django.conf import settings
from borrowing_service.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def build_absolute_url(request, url_name):
    relative_url = reverse(url_name)
    return request.build_absolute_uri(relative_url)


def create_payment_session(request: HttpRequest, borrowing, amount, payment_type):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{payment_type} fee for " f"{borrowing.book.title}",
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=build_absolute_url(request, "borrowing_service:payment-success")
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=build_absolute_url(request, "borrowing_service:payment-cancel")
        + "?session_id={CHECKOUT_SESSION_ID}",
    )

    payment, created = Payment.objects.update_or_create(
        borrowing=borrowing,
        defaults={
            "session_url": session.url,
            "session_id": session.id,
            "money_to_pay": amount,
            "payment_type": payment_type,
            "status": Payment.Status.PENDING.name,
        },
    )

    return payment
