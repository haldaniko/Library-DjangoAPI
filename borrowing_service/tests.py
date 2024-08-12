from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from borrowing_service.models import Borrowing
from books_service.tests import sample_book


BORROWINGS_URL = reverse("borrowing_service:borrowing-list")


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
        print(BORROWINGS_URL)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_borrowing_detail(self):
        borrowing = sample_borrowing(user=self.user)
        url = detail_borrowing_url(borrowing.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
