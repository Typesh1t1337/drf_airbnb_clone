from datetime import date
from rest_framework import serializers
from app.models import Housing, Favorites, Review, HousingPhotos, Booking

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE = 10 * 1024 * 1024


class HousingSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username')
    rating = serializers.SerializerMethodField()
    type_name = serializers.CharField(source='type.name')
    wallpaper = serializers.CharField()
    is_favorite = serializers.BooleanField(read_only=True)

    class Meta:
        model = Housing
        fields = ['id', 'owner_username', 'description',
                  'address', 'city', 'country',
                  'price', 'option', 'rating', 'type_name', "wallpaper", "is_favorite", "name"]

    def get_rating(self, obj):
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
            photo_instance = photos[0]
            if photo_instance.photo and photo_instance.photo.name:
                try:
                    return photo_instance.photo.url
                except ValueError:
                    return None
        return None


class ReviewSerializer(serializers.Serializer):
    housing_id = serializers.IntegerField(required=True)
    rating = serializers.FloatField(required=True)
    text = serializers.CharField(required=True)


class ReviewRetrieveSerializer(serializers.ModelSerializer):
    review_owner = serializers.CharField(source="review_owner.username")
    review_owner_pfp = serializers.SerializerMethodField()
    related_to = serializers.CharField(source="related_to.name")
    review_owner_date_join = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["review_rating", "review_owner",
                  "related_to", "review_date",
                  "review_text", "review_owner_pfp",
                  "review_owner_date_join"]

    def get_review_owner_pfp(self, obj):
        if obj.review_owner.pfp:
            return obj.review_owner.pfp.url
        else:
            return None

    def get_review_owner_date_join(self, obj):
        return obj.review_owner.date_joined.strftime("%m-%d-%Y")


def image_validator(file):
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
               HousingPhotos(
                   housing=housing,
                   photo=image,
                   is_wallpaper=(i == 0),
               )
            )

        HousingPhotos.objects.bulk_create(saved_images)

        return housing


class HousingPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousingPhotos
        fields = ['photo', 'id']


class ReviewsSerializer(serializers.ModelSerializer):
    review_owner = serializers.CharField(source="review_owner.username")
    review_date = serializers.SerializerMethodField()
    review_owner_pfp = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['review_rating', 'review_owner', 'review_date', 'review_text', "review_owner_pfp"]

    def get_review_date(self, obj):
        return obj.review_date.strftime("%m/%d/%Y")

    def get_review_owner_pfp(self, obj):
        if obj.review_owner.pfp:
            return obj.review_owner.pfp.url
        else:
            return None


class HousingDetailsSerializer(serializers.ModelSerializer):
    photos = HousingPhotosSerializer(many=True, read_only=True)
    type = serializers.CharField(source="type.name")
    owner = serializers.CharField(source="owner.username")
    owner_pfp = serializers.SerializerMethodField()
    owner_date_join = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    review_amount = serializers.IntegerField(read_only=True)
    housing_reviews = ReviewsSerializer(many=True, read_only=True)

    class Meta:
        model = Housing
        fields = ('id', 'name', 'description', 'address',
                  'city', 'country', 'price', 'option', 'type', "owner_pfp", "owner_date_join",
                  'owner', 'rating', "photos", "review_amount", "housing_reviews", "conveniences")

    def get_rating(self, obj):
        if obj.rating_amount == 0:
            return 0

        return round(obj.rating_amount / obj.rated_people, 2)

    def get_owner_date_join(self, obj):
        return obj.owner.date_joined.strftime("%m/%d/%Y")

    def get_owner_pfp(self, obj):
        if obj.owner.pfp:
            return obj.owner.pfp.url
        else:
            return None


class UserHousingsSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="type.name")
    wallpaper_photo = serializers.SerializerMethodField()

    class Meta:
        model = Housing
        fields = [
            'id', 'name', 'description',
            'address', 'city', 'country',
            'price', 'option', 'type', "wallpaper_photo"
        ]

    def get_wallpaper_photo(self, obj):
        photos = getattr(obj, "wallpaper_photo", [])
        if photos:
            photo_instance = photos[0]
            if photo_instance.photo and photo_instance.photo.name:
                try:
                    return photo_instance.photo.url
                except ValueError:
                    return None
        return None


class HousingBookSerializer(serializers.Serializer):
    housing_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    bill = serializers.DecimalField(max_digits=10, decimal_places=2)


class HousingBookDetailsSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    wallpaper = serializers.SerializerMethodField()

    class Meta:
        model = Housing
        fields = ('id', 'name', 'address', "city", "country", "wallpaper", "rating")

    def get_rating(self, obj):
        if obj.rating_amount == 0:
            return 0

        return round(obj.rating_amount / obj.rated_people, 2)

    def get_wallpaper(self, obj):
        wallpaper = getattr(obj, "wallpaper", None)
        if wallpaper and wallpaper[0].photo:
            return wallpaper[0].photo.url
        return None


class UserBookingSerializer(serializers.ModelSerializer):
    housing = HousingBookDetailsSerializer()
    booked_date = serializers.SerializerMethodField()
    date_status = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ["id", "check_out_date", "check_in_date", "guests_amount", "bill_to_pay", "housing", "booked_date", "date_status", "status"]

    def get_booked_date(self, obj):
        return obj.created_at.strftime("%m-%d-%Y")

    def get_date_status(self, obj):
        current_time = date.today()
        return obj.check_out_date > current_time


class DeleteBookingSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()


class HousingReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Housing
        fields = ["id", "name", "country", "city", "address"]


class MyHousingReservationSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username")
    first_name = serializers.CharField(source="owner.first_name")
    last_name = serializers.CharField(source="owner.last_name")
    email = serializers.CharField(source="owner.email")
    housing = HousingReservationSerializer()
    booked_date = serializers.SerializerMethodField()
    date_status = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ["id", "owner", "check_out_date",
                  "check_in_date", "guests_amount", "bill_to_pay",
                  "booked_date", "status", "date_status",
                  "housing", "first_name", "last_name", "email"
                  ]

    def get_booked_date(self, obj):
        return obj.created_at.strftime("%m-%d-%Y")

    def get_date_status(self, obj):
        current_time = date.today()
        if obj.check_out_date > current_time:
            return True
        else:
            return False
