from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from books_service.models import Book, CoverType

BOOKS_URL = reverse("books_service:book-list")


def sample_book(**kwargs) -> Book:
    defaults = {
        "title": "Sample book",
        "author": "Smpmle author",
        "cover": CoverType.HARD,
        "inventory": 10,
        "daily_fee": Decimal(value="1.00")
    }
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


class UnauthenticatedReadOnlyBooksTestView(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_unauth_list_required(self) -> None:
        sample_book()
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauth_create_book(self) -> None:
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": CoverType.SOFT,
            "inventory": 5,
            "daily_fee": Decimal("2.00")
        }
        response = self.client.post(BOOKS_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 0)

    def test_unauth_delete_book(self) -> None:
        book = sample_book()
        url = reverse("books_service:book-detail", kwargs={"pk": book.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 1)


class AdminBooksCreateDeleteTestView(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="adminpassword",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self) -> None:
        book_data = {
            "title": "New Book Title",
            "author": "New Author",
            "cover": CoverType.HARD,
            "inventory": 10,
            "daily_fee": Decimal("0.25"),
        }

        response = self.client.post(BOOKS_URL, book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(pk=response.data["id"])
        for key in book_data:
            self.assertEqual(book_data[key], getattr(book, key))

    def test_auth_delete_book(self) -> None:
        book = sample_book()
        url = reverse("books_service:book-detail", kwargs={"pk": book.id})
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )
