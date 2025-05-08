from django.contrib.auth import get_user_model
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from serializers import HousingSerializer, BanSerializer, UserSerializer
from app.models import Housing
from django.shortcuts import get_object_or_404
from filters import UserFilter


class NotApprovedHousingListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        housings = Housing.objects.all().filter(approved=False).select_related("owner", "type")
        serializer = HousingSerializer(housings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApprovedHousingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = HousingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        housing_id = serializer.validated_data.get("housing_id", None)

        housing = Housing.objects.get(pk=housing_id)
        housing.status = True
        housing.save()

        return Response(
            {
                "status": "Success"
            }, status=status.HTTP_200_OK
        )


class BanUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = BanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data.get("user_id", None)
        user = get_object_or_404(get_user_model(), pk=user_id)
        if not user.is_banned:
            user.is_banned = True
        else:
            user.is_banned = False

        user.save(update_fields=["is_banned"])
        return Response(
            {
                "status": "Success",
            }, status=status.HTTP_200_OK
        )


class PaginationUsers(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class AllUsersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer
    pagination_class = PaginationUsers
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilter

    def get_queryset(self):
        queryset = get_user_model().objects.filter(is_staff=True)
        return queryset
