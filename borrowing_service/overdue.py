from datetime import datetime

from borrowing_service.helpers.telegram import send_message
from borrowing_service.models import Borrowing


def check_overdue_borrowings():
    today = datetime.today().date()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date__isnull=True, expected_return_date__lte=today
    )
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            send_telegram_notification(borrowing)
        return f"{len(overdue_borrowings)} overdue borrowings notified."
    else:
        send_message("No borrowings overdue today")
    return "No borrowings overdue today"


def send_telegram_notification(borrowing: Borrowing):
    user = borrowing.user
    book = borrowing.book
    message = (
        f"📚 Book Borrowing Details\n\n"
        f"User: {user.first_name} {user.last_name}\n"
        f"Book: {book.title}\n"
        f"Author: {book.author}\n"
        f"Borrow Date: {borrowing.borrow_date}\n"
        f"Expected Return Date: {borrowing.expected_return_date}\n"
    )
    send_message(message)
