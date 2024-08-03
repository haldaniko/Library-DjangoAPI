from celery import shared_task

from borrowing_service.overdue import check_overdue_borrowings


@shared_task
def tg_notification():
    check_overdue_borrowings()
