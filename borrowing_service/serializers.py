from django.db.transaction import atomic
from rest_framework import serializers

from books_service.serializers import BookSerializer
from user.serializers import UserSerializer
from .models import Borrowing, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("status", "payment_type", "borrowing", "session_url", "session_id", "money_to_pay")


class BorrowingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date")

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)

        Borrowing.validate_borrowing(
            attrs["book"].inventory,
            serializers.ValidationError
        )
        return data

    @atomic
    def create(self, validated_data):

        print("---->", self.context["request"].user)

        book = validated_data["book"]
        expected_return_date = validated_data["expected_return_date"]

        borrowing = Borrowing.objects.create(
            user=self.context["request"].user,
            book=book,
            expected_return_date=expected_return_date,
        )

        book.inventory -= 1
        book.save()

        return borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(
        read_only=True,
        source="book.title"
    )
    user = serializers.CharField(
        read_only=True,
        source="user.email"
    )

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
