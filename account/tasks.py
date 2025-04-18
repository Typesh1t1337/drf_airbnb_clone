import hashlib

from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from airbnb.settings import EMAIL_HOST_USER
from celery import shared_task
import random
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .storage import PFPStorage


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


@shared_task
def add_pfp_task(user_id, image_data) -> bool:
    try:
        storage = PFPStorage()
        user = get_user_model().objects.get(pk=user_id)
        unique_has = hashlib.md5(image_data).hexdigest()[:10]
        file_name = f"{user_id}_{unique_has}.jpg"

        file_path =storage.save(file_name, ContentFile(image_data))
        file_url = storage.url(file_path)
        file_url = file_url.replace("aws", "127.0.0.1")

        user.pfp = file_url
        user.save(update_fields=['pfp'])

        return True
    except Exception as e:
        print(str(e))
        return False
