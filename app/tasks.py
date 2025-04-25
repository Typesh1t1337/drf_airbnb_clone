from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from airbnb.settings import EMAIL_HOST_USER
from .models import Booking


@shared_task
def book_notification_email(user_id: int, booking_id: int) -> bool:
    user = get_user_model().objects.get(pk=user_id)
    subject = "Booking Notification"
    recipient_email = [user.email]

    booking = Booking.objects.select_related("housing").get(id=booking_id)
    information_text = f"Hi there {user.first_name}, The booking of {booking.housing.name} has been completed. Have a nice trip!"

    credentials = {
        "booking": booking,
        "information_text": information_text
    }

    html_content = render_to_string("email/notification.html", credentials)

    try:
        email_message = EmailMessage(subject, html_content, EMAIL_HOST_USER, recipient_email)
        email_message.content_subtype = "html"
        email_message.send()
        return True
    except Exception as e:
        print(e)
        return False




