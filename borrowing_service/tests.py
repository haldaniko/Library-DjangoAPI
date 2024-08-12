from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from borrowing_service.models import Borrowing, Payment
from books_service.tests import sample_book

BORROWINGS_URL = reverse("borrowing_service:borrowing-list")
PAYMENTS_LIST = reverse("borrowing_service:payment-list")


def sample_borrowing(**kwargs) -> Borrowing:
    user = kwargs.get("user", get_user_model())
    book = sample_book()

    borrow_date = kwargs.get("borrowing_date", datetime.today().date())
    expected_return_date = kwargs.get(
        "expected_return_date", borrow_date + timedelta(days=7)
    )
    defaults = {
        "user": user,
        "book": book,
        "borrow_date": borrow_date,
        "expected_return_date": expected_return_date,
    }
    defaults.update(kwargs)

    return Borrowing.objects.create(**defaults)


def detail_borrowing_url(borrowing_id: int):
    return reverse("borrowing_service:borrowing-detail", kwargs={"pk": borrowing_id})


def sample_payment(borrowing=None, **kwargs) -> Payment:

    defaults = {
        "session_url": "http://example.com",
        "session_id": "sess_123456789",
        "money_to_pay": 10.00,
        "payment_type": Payment.Type.PAYMENT.name,
        "status": Payment.Status.PAID.name,
        "borrowing": borrowing,
    }
    defaults.update(kwargs)
    return Payment.objects.create(**defaults)


def detail_payment_url(payment_id: int):
    return reverse("borrowing_service:payment-detail", kwargs={"pk": payment_id})


class UnauthenticatedUserBorrowingsTestView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword"
        )

    def test_unauth_borrowing_list(self):
        sample_borrowing(user=self.user)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserBorrowingsTestView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="admin@example.com",
            password="adminpassword",
            is_staff=True,
        )
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="userpassword"
        )
        self.client.force_authenticate(self.admin)

    def test_admin_borrowing_list(self):
        sample_borrowing(user=self.user)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_borrowing_detail(self):
        borrowing = sample_borrowing(user=self.user)
        url = detail_borrowing_url(borrowing.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UnauthenticatedUserPaymentTestView(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpassword"
        )

    def test_unauth_payment_list(self):
        borrowing: Borrowing = sample_borrowing(user=self.user)
        sample_payment(borrowing=borrowing)
        response = self.client.get(PAYMENTS_LIST)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserPaymentTestView(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="userpassword"
        )
        self.user_2 = get_user_model().objects.create_user(
            email="user2@example.com",
            password="user2password"
        )
        self.client.force_authenticate(user=self.user)

    def test_have_not_access_to_all_payments(self) -> None:
        borrowing = sample_borrowing(user=self.user_2)
        payment = sample_payment(borrowing=borrowing)

        response = self.client.get(PAYMENTS_LIST)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(detail_payment_url(payment.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
