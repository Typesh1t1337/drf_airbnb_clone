from celery import shared_task
from django.core.files.base import ContentFile

from app.models import Housing,HousingPhotos
from .storage import HousingStorage
import uuid
import hashlib


@shared_task
def upload_photos(housing_id, images_data) -> bool:
    print(images_data)
    storage = HousingStorage()
    housing_obj = Housing.objects.get(pk=housing_id)
    for image in images_data:
        image_content = image['photo']
        unique_hash = hashlib.md5(image_content).hexdigest()[:10]
        file_name = f"{housing_id}/{unique_hash}.jpg"

        file_path = storage.save(file_name, ContentFile(image_content))
        file_url = storage.url(file_path)
        file_url = file_url.replace("aws", "127.0.0.1")

        HousingPhotos.objects.create(
            housing=housing_obj,
            photo=file_url,
            owner=housing_obj.owner,
            is_wallpaper=image['is_wallpaper'],
        )

    return True


