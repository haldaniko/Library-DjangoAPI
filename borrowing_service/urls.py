from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing_service.views import PaymentViewSet, BorrowingViewSet, BorrowingReturnAPIView

router = DefaultRouter()
router.register(r"payments", PaymentViewSet)
router.register(r"borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "borrowings/<int:pk>/return/",
        BorrowingReturnAPIView.as_view(),
        name="borrowing-return"
    ),
]

app_name = "borrowing_service"
