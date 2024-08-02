from datetime import date
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from books_service.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} borrowed {self.book} on {self.borrow_date}"

    @staticmethod
    def validate_borrowing(
            inventory,
            error_to_raise
    ) -> None:
        if inventory == 0:
            raise error_to_raise(
                {"book": "Book inventory is zero. Cannot borrow this book."}
            )

    def clean(self) -> None:
        Borrowing.validate_borrowing(
            self.book.inventory,
            ValueError
        )

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)

    def return_book(self) -> None:
        self.actual_return_date = date.today()
        self.book.inventory += 1
        self.book.save()
        self.save()

    def calculate_total_fee(self) -> Decimal:
        end_date = self.expected_return_date
        total_days = (end_date - self.borrow_date).days
        total_fee = Decimal(total_days) * self.book.daily_fee

        return total_fee


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'

    class Type(models.TextChoices):
        PAYMENT = 'PAYMENT', 'Payment'
        FINE = 'FINE', 'Fine'

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    payment_type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.PAYMENT
    )
    borrowing = models.OneToOneField(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=200)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return f"Payment for {self.borrowing} - Status: {self.status}, Type: {self.payment_type}"