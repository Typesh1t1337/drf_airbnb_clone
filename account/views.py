from django.contrib.auth import authenticate
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import *
from .tasks import email_verification
from datetime import timedelta


class RegisterView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        if get_user_model().objects.filter(Q(username=username) | Q(email=email)).exists():
            return Response({'error': 'Email or username already registered'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password)

        email_verification.delay(email=user.email)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response({
            "status": user.is_verified,
            "username": user.username
        }, status=status.HTTP_201_CREATED)

        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=False,
            max_age=timedelta(days=1),
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=False,
            max_age=timedelta(days=30),
        )

        return response


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.data['username']
        password = serializer.data['password']

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response(
            {
                "status": user.is_verified,
                "username": user.username
            }, status=status.HTTP_200_OK
        )

        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=False,
            max_age=timedelta(days=1),
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=False,
            max_age=timedelta(days=30),
        )

        return response


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        cache_key = f"user_{username}"
        data = cache.get(cache_key)

        user = get_object_or_404(get_user_model(), username=username)

        serializer = UserInfoSerializer(user).data

        if data:
            return Response(data, status=status.HTTP_200_OK)

        cache.set(cache_key, serializer, 600)

        return Response(serializer, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(
            {
                "status": "success",
            }, status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class EditProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(f"user_{user.username}")
        serializer.save()
        return Response(
            {
                "status": "success",
            }, status=status.HTTP_200_OK
        )