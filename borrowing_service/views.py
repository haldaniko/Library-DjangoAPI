from rest_framework import viewsets
from .models import Borrowing, Payment
from .serializers import BorrowingSerializer, PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


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
