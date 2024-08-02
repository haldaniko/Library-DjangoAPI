from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from permissions import IsAdminOrReadOnly
from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)
