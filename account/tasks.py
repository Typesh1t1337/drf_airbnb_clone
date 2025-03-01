

from celery import shared_task
import random

from django.contrib.auth import get_user_model
from django.utils.timezone import now


@shared_task
def email_verification(email: str) -> bool:
    digit_code = random.randint(100000, 999999)

    user = get_user_model().objects.get(email=email)

    user.verification_code = digit_code
    user.last_verification = now()
    user.save(update_fields=['verification_code', 'last_verification'])

    return True
