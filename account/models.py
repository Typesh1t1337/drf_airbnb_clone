from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from .storage import PFPStorage


def pfp_upload_location(instance, filename):
    return f"{instance.pk}/{filename}"


class User(AbstractUser):
    is_verified = models.BooleanField(default=False)
    verification_code = models.IntegerField(null=True)
    pfp = models.TextField(null=True)
    last_verification = models.DateTimeField(null=True, blank=True)
    about_me = models.TextField(blank=True)
