from rest_framework import serializers

from account.models import User
from app.models import Housing


class HousingSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username')
    type = serializers.CharField(source='type.name')

    class Meta:
        model = Housing
        fields = ['id', 'name', 'address', 'city', "country", "owner", "type"]


class HousingIdSerializer(serializers.Serializer):
    housing_id = serializers.IntegerField()


class BanSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', "pfp", "is_banned", "is_active"]
