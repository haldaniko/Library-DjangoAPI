from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .models import Borrowing, Payment
from .serializers import (
    BorrowingSerializer,
    BorrowingReturnSerializer,
    PaymentSerializer, BorrowingDetailSerializer, BorrowingListSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        is_active = self.request.query_params.get('is_active')

        queryset = self.queryset

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer


class BorrowingReturnAPIView(generics.UpdateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer

    def put(self, request, *args, **kwargs) -> Response:
        borrowing = self.get_object()
        serializer = self.get_serializer(
            borrowing,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.save()
        return_date = serializer.validated_data.get('return_date')
        if return_date:
            borrowing.return_date = return_date
            borrowing.save()

        return Response(
            {"detail": "Borrowing updated and book inventory increased."},
            status=status.HTTP_200_OK,
        )


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
