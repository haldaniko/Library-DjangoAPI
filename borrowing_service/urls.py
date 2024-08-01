from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowing_service.views import PaymentViewSet, BorrowingViewSet

router = DefaultRouter()
router.register(r"payments", PaymentViewSet)
router.register(r"borrowings", BorrowingViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowing_service"
