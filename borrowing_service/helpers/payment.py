import stripe
from django.conf import settings

from borrowing_service.models import Payment


def create_payment_session(borrowing, amount, payment_type):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{payment_type} fee for "
                        f"{borrowing.book.title}",
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=(
            settings.STRIPE_SUCCESS_URL
            + "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url=(
            settings.STRIPE_CANCEL_URL
            + "?session_id={CHECKOUT_SESSION_ID}"
        ),
    )

    payment, created = Payment.objects.get_or_create(
        borrowing=borrowing,
        defaults={
            "session_url": session.url,
            "session_id": session.id,
            "money_to_pay": amount,
            "type": payment_type,
        },
    )
    if not created:
        payment.session_url = session.url
        payment.session_id = session.id
        payment.money_to_pay = amount
        payment.type = payment_type
        payment.save()

    return payment