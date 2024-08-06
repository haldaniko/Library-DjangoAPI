from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing_service.views import PaymentViewSet, BorrowingViewSet, BorrowingReturnAPIView, PaymentSuccessView, \
    PaymentCancelView, PaymentRenewalView

router = DefaultRouter()
router.register(r"payments", PaymentViewSet)
router.register(r"borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("borrowings/<int:pk>/return/",
         BorrowingReturnAPIView.as_view(),
         name="borrowing-return"),
    path("payments/", include(router.urls)),
    path("payments/renew/",
         PaymentRenewalView.as_view(),
         name="payment-renewal"),
    path("payment/success/",
         PaymentSuccessView.as_view(),
         name="payment-success"),
    path("payment/cancel/",
         PaymentCancelView.as_view(),
         name="payment-cancel"),
]

app_name = "borrowing_service"
