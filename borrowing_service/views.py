from rest_framework import viewsets, status, generics, mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers.payment import create_payment_session
from .helpers.telegram import send_message
from .models import Borrowing, Payment
from .serializers import (
    BorrowingReturnSerializer,
    PaymentSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    PaymentDetailSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingCreateSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")
        user = self.request.user
        queryset = self.queryset

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to view this data.")
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if is_active and is_active.lower() == "true":
            queryset = queryset.filter(actual_return_date=None)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.validated_data["book"]
        expected_return_date = serializer.validated_data["expected_return_date"]
        user = self.request.user

        pending_payments = Payment.objects.filter(
            borrowing__user=user, status="PENDING" or "EXPIRED"
        )
        if pending_payments:
            raise ValidationError(
                "You have pending/expired payments. "
                "You cannot borrow new books until they are paid."
            )

        message = (
            f"📚 Book Borrowing Details\n\n"
            f"User: {user.first_name} {user.last_name}\n"
            f"Book Title: {book.title}\n"
            f"Author: {book.author}\n"
            f"Expected Return Date: {expected_return_date}\n"
        )
        send_message(message)

        borrowing = serializer.save(user=user)

        total_fee = borrowing.calculate_total_fee()
        create_payment_session(
            self.request, borrowing, total_fee, Payment.Type.PAYMENT.name
        )
        payment = Payment.objects.get(borrowing=borrowing)
        return Response(
            {
                "detail": "Borrowing created successfully",
                "stripe_session_url": payment.session_url,
            },
            status=status.HTTP_201_CREATED,
        )


class BorrowingReturnAPIView(generics.UpdateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer

    def put(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.save()

        if borrowing.actual_return_date > borrowing.expected_return_date:
            total_fee = borrowing.calculate_overdue_fee()
            payment = create_payment_session(
                self.request, borrowing, total_fee, Payment.Type.PAYMENT.name
            )
            return Response(
                {
                    "detail": "Borrowing updated and book inventory increased.",
                    "fine": f"The book return period has expired. You have to pay fine: {total_fee}",
                    "stripe_session_url": payment.session_url,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Borrowing updated and book inventory increased."},
            status=status.HTTP_200_OK,
        )


class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.all().select_related()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if not user.is_staff:
            return queryset.filter(borrowing__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentSerializer
        return PaymentDetailSerializer


class PaymentRenewalView(APIView):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        payment = Payment.objects.filter(status="EXPIRED", borrowing__user=user).first()
        if payment:
            new_session = create_payment_session(
                self.request,
                payment.borrowing,
                payment.money_to_pay,
                Payment.Type.PAYMENT.name,
            )

            payment.status = new_session
            payment.save()

            return Response(
                {
                    "detail": "Payment session renewed.",
                    "session_id": new_session.id,
                    "session_url": new_session.url,
                }
            )
        return Response(
            {"detail": "No expired payment session found for renewal."},
            status=status.HTTP_404_NOT_FOUND,
        )


class PaymentSuccessView(APIView):
    @staticmethod
    def get(request, *args, **kwargs) -> Response:
        session_id = request.query_params.get("session_id")
        payment = Payment.objects.get(session_id=session_id)
        payment.status = Payment.Status.PAID.name
        payment.save()
        return Response({"detail": "Payment succeeded!"})


class PaymentCancelView(APIView):
    @staticmethod
    def get(request, *args, **kwargs) -> Response:
        return Response(
            {
                "detail": "Your payment session is still "
                "available for 24 hours. Please complete your "
                "payment within this period."
            }
        )
