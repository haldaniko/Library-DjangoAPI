from django.contrib import admin
from .models import Borrowing, Payment


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "book",
        "user",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "payment_type",
        "borrowing",
        "session_url",
        "session_id",
        "money_to_pay",
    )
