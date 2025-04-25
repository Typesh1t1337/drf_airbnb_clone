from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from airbnb.settings import EMAIL_HOST_USER
from celery import shared_task
import random
from django.contrib.auth import get_user_model
from django.utils.timezone import now


@shared_task
def email_verification(email: str) -> bool:
    subject = "Verification code"
    recipient_list = [email]
    digit_code = random.randint(100000, 999999)

    user = get_user_model().objects.get(email=email)
    user.verification_code = digit_code
    user.last_verification = now()
    user.save(update_fields=['verification_code', 'last_verification'])

    credentials = {
        "full_name": user.first_name + " " + user.last_name,
        "code": digit_code,
    }

    html_content = render_to_string("email/verify.html", credentials)

    email_message = EmailMessage(subject, html_content, EMAIL_HOST_USER, recipient_list)
    email_message.content_subtype = "html"
    email_message.send()

    return True

