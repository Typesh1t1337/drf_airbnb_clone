from django.contrib.auth import get_user_model
from rest_framework import serializers, status


class UserRegisterSerializer(serializers.Serializer):
   username = serializers.CharField(required=True)
   email = serializers.EmailField(required=True)
   password = serializers.CharField(min_length=6, write_only=True)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserInfoSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    join_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', "photo", 'email', 'first_name', 'last_name', 'about_me', "join_date"]

    def get_join_date(self, obj):
        return obj.date_joined.strftime('%m/%d/%Y')

    def get_photo(self, obj):
        return obj.pfp.url if obj.pfp else None


def image_validator(file):
    allow = ["image/jpeg", "image/png", "image/webp"]
    max_size = 10 * 1024 * 1024

    if file.size > max_size:
        raise serializers.ValidationError(
            "File too large. Max allowed size is {}".format(max_size)
        )
    if file.content_type not in allow:
        raise serializers.ValidationError(
            "Content type must be one of {}".format(allow)
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "about_me", "pfp"]

    def update(self, instance, validated_data):
        for attr in ['about_me', 'first_name', 'last_name', 'pfp']:
            value = validated_data.get(attr, None)
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6)
    code = serializers.CharField(min_length=6)
    email = serializers.EmailField(required=True)

