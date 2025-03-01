from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import *

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.data.get('username', '')
            email = serializer.data.get('email', '')
            first_name = serializer.data.get('first_name', '')
            last_name = serializer.data.get('last_name', '')
            password = serializer.data.get('password', '')

            if get_user_model().objects.filter(username=username).exists():
                return Response({
                    'error': 'Username already exists'
                }, status=status.HTTP_400_BAD_REQUEST)

            if get_user_model().objects.filter(email=email).exists():
                return Response({
                    'error': 'Email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)


            user = get_user_model().objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password)

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
            return Response(data,status=status.HTTP_200_OK)

        cache.set(cache_key, serializer)

        return Response(serializer, status=status.HTTP_200_OK)


