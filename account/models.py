from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from .storage import PFPStorage
def pfp_upload_location(instance, filename):
    return f"{instance.pk}/{filename}"

class User(AbstractUser):
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True)
    pfp = models.ImageField(upload_to=pfp_upload_location,validators=[FileExtensionValidator(["jpeg","png","jpg","webp"])], null=True, storage=PFPStorage())
    last_verification = models.DateTimeField(null=True, blank=True)


