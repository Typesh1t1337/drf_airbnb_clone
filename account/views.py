from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import *
from .tasks import email_verification

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            username = validated_data['username']
            email = validated_data['email']
            first_name = validated_data['first_name']
            last_name = validated_data['last_name']
            password = validated_data['password']


            user = get_user_model().objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password)


            email_verification.delay(email=user.email)

            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return Response(
                {
                    'accessToken': access,
                    'refreshToken': str(refresh)
                 }
                , status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self,request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.data['username']
            password = serializer.data['password']

            if not get_user_model().objects.filter(username=username).exists():
                return Response({
                    'error': 'Username does not exist'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)

            if user is None:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)

            return Response(
                {
                    'accessToken': access,
                    'refreshToken': str(refresh)
                }, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        cache_key = f"user_{user.id}"
        data = cache.get(cache_key)

        serializer = UserInfoSerializer(user).data

        if data:
            return Response(data, status=status.HTTP_200_OK)

        cache.set(cache_key, serializer)

        return Response(serializer, status=status.HTTP_200_OK)

