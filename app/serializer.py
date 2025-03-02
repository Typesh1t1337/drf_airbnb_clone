from rest_framework import serializers

from app.models import Housing, Favorites, Review, HousingPhotos


class HousingSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username')
    rating = serializers.SerializerMethodField()
    type_name = serializers.CharField(source='type.name')

    class Meta:
        model = Housing
        fields = ['id', 'owner_username', 'description',
                  'address', 'city', 'country',
                  'price', 'option', 'rating', 'type_name']


    def get_rating(self,obj):

        if obj.rating_amount == 0:
            return 0

        return round(obj.rating_amount / obj.rated_people, 2)



class AddToFavoritesSerializer(serializers.Serializer):
    housing_id = serializers.IntegerField()


class FavoritesListSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="favorites_owner.username")
    housing_id = serializers.IntegerField(source="favorites_housing.id")
    housing_price = serializers.IntegerField(source="favorites_housing.price")
    housing_type = serializers.CharField(source="favorites_housing.type.name")
    housing_address = serializers.CharField(source="favorites_housing.address")
    housing_city = serializers.CharField(source="favorites_housing.city")
    housing_country = serializers.CharField(source="favorites_housing.country")
    class Meta:
        model = Favorites
        fields = ['owner', 'housing_id', 'housing_price', 'housing_type','housing_address','housing_city', 'housing_country']



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



class HousingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HousingPhotos
        fields = ['image', 'is_wallpaper']


class AddHousingSerializer(serializers.ModelSerializer):
    images = HousingImageSerializer(many=True, required=False)
    class Meta:
        model = Housing
        fields = ['images', 'name', 'description', 'address', 'city', 'country', 'price', 'option', 'type']
