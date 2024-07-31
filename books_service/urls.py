from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books_service.views import BookViewSet

router = DefaultRouter()
router.register(r"books", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "books_service"
