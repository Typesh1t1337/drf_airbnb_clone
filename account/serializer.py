from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from .tasks import add_pfp_task


class UserRegisterSerializer(serializers.Serializer):
   username = serializers.CharField(required=True)
   email = serializers.EmailField(required=True)
   password = serializers.CharField(min_length=6, write_only=True)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserInfoSerializer(serializers.ModelSerializer):
    join_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'about_me', "join_date"]

    def get_join_date(self, obj):
        return obj.date_joined.strftime('%m/%d/%Y')


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
    photo = serializers.ImageField(validators=[image_validator])
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "about_me", "photo"]

    def update(self, instance, validated_data):
        about_me = validated_data.get('about_me', None)
        first_name = validated_data.get('first_name', None)
        last_name = validated_data.get('last_name', None)
        pfp = validated_data.pop('photo', None)

        if about_me is not None:
            instance.about_me = about_me

        if first_name is not None:
            instance.first_name = first_name

        if last_name is not None:
            instance.last_name = last_name

        if pfp is not None:
            image = pfp.read()
            add_pfp_task.delay(instance.id, image)

        instance.save()
        return instance

