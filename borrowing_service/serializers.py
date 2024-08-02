from rest_framework import serializers

from books_service.serializers import BookSerializer
from user.serializers import UserSerializer
from .models import Borrowing, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("status", "payment_type", "borrowing", "session_url", "session_id", "money_to_pay")


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("borrow_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Borrowing
        fields = ("borrow_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = ("borrow_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ['actual_return_date']
