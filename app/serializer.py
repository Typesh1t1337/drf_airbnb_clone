from rest_framework import serializers

from app.models import Housing


class HousingSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username')
    rating = serializers.SerializerMethodField()
    class Meta:
        model = Housing
        fields = ['id', 'owner_username', 'description', 'address', 'city', 'country', 'price', 'option', 'rating']


    def get_rating(self,obj):

        if obj.rating_amount == 0:
            return 0

        return round(obj.rating_amount / obj.rated_people, 2)
