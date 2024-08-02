from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Borrowing, Payment
from .serializers import BorrowingSerializer, BorrowingReturnSerializer, PaymentSerializer


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
