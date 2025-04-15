from django.contrib.auth import get_user_model
from django.db import models
from .storage import HousingStorage


class Housing(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    description = models.TextField(null=False,blank=False)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    rated_people = models.IntegerField(default=0)
    rating_amount = models.FloatField(default=0)
    price = models.IntegerField(default=0)
    option = models.CharField(choices=(
        ('Per day', 'per day'), ('Per week', 'per week'), ('Per month', 'per month'),
    ), null=False, blank=False)
    type = models.ForeignKey("TypeOfHousing", on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


class TypeOfHousing(models.Model):
    name = models.CharField(max_length=100)


class HousingPhotos(models.Model):
    housing = models.ForeignKey(Housing, on_delete=models.CASCADE, related_name='photos')
    photo = models.TextField(max_length=500, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_wallpaper = models.BooleanField(default=False)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)

    def delete(self,*args, **kwargs):
        if self.photo:
            storage = HousingStorage()
            storage.delete(self.photo)

        super().delete(*args, **kwargs)


class Review(models.Model):
    review_owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=False, blank=False)
    review_text = models.TextField(null=False, blank=False)
    review_date = models.DateField(null=False, blank=False, auto_now=True)
    review_rating = models.IntegerField(null=False, blank=False)
    related_to = models.ForeignKey(Housing, on_delete=models.CASCADE, null=False, blank=False, related_name='reviews')


class Favorites(models.Model):
    favorites_owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=False, blank=False)
    favorites_housing = models.ForeignKey(Housing, on_delete=models.CASCADE, null=False, blank=False)
