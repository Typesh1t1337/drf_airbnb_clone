from rest_framework import serializers

from app.models import Housing, Favorites, Review, HousingPhotos
from .tasks import upload_photos


class HousingSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username')
    rating = serializers.SerializerMethodField()
    type_name = serializers.CharField(source='type.name')
    wallpaper = serializers.CharField(read_only=True)
    is_favorite = serializers.BooleanField(read_only=True)

    class Meta:
        model = Housing
        fields = ['id', 'owner_username', 'description',
                  'address', 'city', 'country',
                  'price', 'option', 'rating', 'type_name', "wallpaper", "is_favorite", "name"]

    def get_rating(self,obj):
        if obj.rating_amount == 0:
            return 0

        return round(obj.rating_amount / obj.rated_people, 2)


class AddToFavoritesSerializer(serializers.Serializer):
    housing_id = serializers.IntegerField()


class HousingFavoritesSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='type.name')

    class Meta:
        model = Housing
        fields = ["id", "price", "type", "address", "city", "country", "name", "option"]


class FavoritesListSerializer(serializers.ModelSerializer):
    housing = HousingFavoritesSerializer(source="favorites_housing")
    wallpaper_photo = serializers.SerializerMethodField()

    class Meta:
        model = Favorites
        fields = ["housing", "wallpaper_photo"]

    def get_wallpaper_photo(self, obj):
        photos = getattr(obj.favorites_housing, "wallpaper_photo", [])
        if photos:
            return photos[0].photo
        return None


class ReviewSerializer(serializers.Serializer):
    housing_id = serializers.IntegerField(required=True)
    rating = serializers.FloatField(required=True)
    text = serializers.CharField(required=True)


class ReviewRetrieveSerializer(serializers.ModelSerializer):
    review_owner = serializers.CharField(source="review_owner.username")
    related_to = serializers.CharField(source="related_to.name")

    class Meta:
        model = Review
        fields = ["review_rating", "review_owner", "related_to", "review_date", "review_text"]


def image_validator(file):
    ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
    MAX_FILE_SIZE = 10 * 1024 * 1024

    if file.size > MAX_FILE_SIZE:
        raise serializers.ValidationError(
            "File too large. Max allowed size is {}".format(MAX_FILE_SIZE)
        )
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise serializers.ValidationError(
            "Content type must be one of {}".format(ALLOWED_CONTENT_TYPES)
        )


class HousingImageSerializer(serializers.Serializer):
    photo = serializers.ImageField(required=True, validators=[image_validator])


class AddHousingSerializer(serializers.ModelSerializer):
    images = HousingImageSerializer(many=True, required=False)

    class Meta:
        model = Housing
        fields = ['images', 'name', 'description', 'address', 'city', 'country', 'price', 'option', 'type']

    def create(self, validated_data):
        images_data = self.context['request'].data.getlist('images')

        housing = Housing.objects.create(**validated_data)

        saved_images = []

        for i, image in enumerate(images_data):

            saved_images.append(
                {
                    "photo": image.read(),
                    "is_wallpaper": (i==0)
                }
            )

        upload_photos.delay(housing.id, saved_images)

        return housing


class HousingPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousingPhotos
        fields = ['photo', 'id']


class ReviewsSerializer(serializers.ModelSerializer):
    review_owner = serializers.CharField(source="review_owner.username")
    review_date = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['review_rating', 'review_owner', 'review_date', 'review_text']

    def get_review_date(self, obj):
        return obj.review_date.strftime("%m/%d/%Y")


class HousingDetailsSerializer(serializers.ModelSerializer):
    photos = HousingPhotosSerializer(many=True, read_only=True)
    type = serializers.CharField(source="type.name")
    owner = serializers.CharField(source="owner.username")
    rating = serializers.SerializerMethodField()
    review_amount = serializers.IntegerField(read_only=True)
    housing_reviews = ReviewsSerializer(many=True, read_only=True)

    class Meta:
        model = Housing
        fields = ('id', 'name', 'description', 'address',
                  'city', 'country', 'price', 'option', 'type',
                  'owner', 'rating', "photos", "review_amount", "housing_reviews")

    def get_rating(self, obj):
        if obj.rating_amount == 0:
            return 0

        return round(obj.rating_amount / obj.rated_people, 2)
