from django.core.cache import cache
from django.db.models import OuterRef, Subquery, Exists, Count, Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .filters import HousingFilter
from .serializer import *


class HousingPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class RetrieveAllHousingView(generics.ListAPIView):
    permission_classes = [AllowAny]
    pagination_class = HousingPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    queryset = Housing.objects.all()
    serializer_class = HousingSerializer
    filterset_class = HousingFilter

    def get_queryset(self):
        user = self.request.user
        wallpaper_photo = HousingPhotos.objects.filter(
            housing=OuterRef('pk'),
            is_wallpaper=True,
        ).values("photo")[:1]

        basic_queryset = Housing.objects.all().select_related("owner").annotate(
            wallpaper=Subquery(wallpaper_photo)
        ).order_by("-created_at")

        if user.is_authenticated:
            is_favorite = Favorites.objects.filter(
                favorites_owner=user,
                favorites_housing=OuterRef('pk'),
            )
            return basic_queryset.annotate(
                is_favorite=Exists(is_favorite)
            ).exclude(owner=user)

        return basic_queryset


class FavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = AddToFavoritesSerializer(data=request.data)

        if serializer.is_valid():
            housing_id = serializer.validated_data['housing_id']

            housing_obj = Housing.objects.get(pk=housing_id)

            favorites_exists = Favorites.objects.filter(favorites_housing=housing_obj, favorites_owner=user).exists()

            if favorites_exists:
                return Response(
                    {
                        "message": "Favorites already added.",
                    }, status=status.HTTP_400_BAD_REQUEST,
                )

            Favorites.objects.create(favorites_housing=housing_obj, favorites_owner=user)

            cache.delete(f'favorites_{user.username}')

            return Response(
                {
                    "message": "Favorites added.",
                }, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        cache_key = f"favorites_{user.username}"

        housing_id = request.query_params.get('housing_id', None)

        if not housing_id:
            return Response(
                {
                    "message": "Housing ID not provided."
                }, status=status.HTTP_400_BAD_REQUEST
            )

        favorite = Favorites.objects.filter(
            favorites_housing_id=housing_id, favorites_owner=user
        )

        if not favorite.exists():
            return Response({
                "message": "Favorites not added.",
            }, status=status.HTTP_400_BAD_REQUEST)

        favorite.delete()
        cache.delete(cache_key)

        return Response({
            "message": "Favorites deleted.",
        }, status=status.HTTP_200_OK)

    def get(self, request):
        user = request.user

        cache_key = f"favorites_{user.username}"
        data = cache.get(cache_key)

        if data:
            return Response(data=data, status=status.HTTP_200_OK)

        wallpapers = HousingPhotos.objects.filter(is_wallpaper=True)

        favorites = ((Favorites.objects.filter(favorites_owner=user).
                     select_related("favorites_housing", "favorites_housing__type")).
                     prefetch_related(Prefetch("favorites_housing__photos", queryset=wallpapers, to_attr="wallpaper_photo")))

        if not favorites.exists():
            return Response({
                "message": "You don't have any favorites.",
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = FavoritesListSerializer(favorites, many=True).data

        cache.set(cache_key, serializer, 600)

        return Response(serializer, status=status.HTTP_200_OK)


class WriteReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            housing_id = serializer.validated_data['housing_id']
            rating = serializer.validated_data['rating']
            text = serializer.validated_data['text']

            try:
                housing_obj = Housing.objects.get(pk=housing_id)
            except Housing.DoesNotExist:
                return Response(
                    {
                        "message": f"Housing not founded by id: {housing_id} ."
                    }, status=status.HTTP_404_NOT_FOUND,
                )

            review = Review.objects.filter(related_to=housing_obj, review_owner=user)

            if review.exists():
                return Response(
                    {
                        "message": "Review already added.",
                    }, status=status.HTTP_400_BAD_REQUEST,
                )

            Review.objects.create(related_to=housing_obj, review_owner=user, review_text=text, review_rating=rating)

            housing_obj.rated_people += 1
            housing_obj.rating_amount += rating

            housing_obj.save(update_fields=["rating_amount", "rated_people"])

            return Response(
                {
                    "message": "Review added.",
                }, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class RetrieveReviewView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="housing_id",
                in_=openapi.IN_QUERY,
                description="Retrieve reviews via housing id.",
                required=True,
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="page",
                in_=openapi.IN_QUERY,
                description="Page number, pagination",
                required=True,
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={200: openapi.Response("Successful Response", ReviewRetrieveSerializer(many=True))}
    )
    def get(self, request):

        housing_id = request.query_params.get('housing_id', None)

        if not housing_id:
            return Response(
                {
                    "message": "Housing not found.",
                }, status=status.HTTP_404_NOT_FOUND,
            )

        try:
            housing_id = int(housing_id)
        except ValueError:
            return Response({
                "message": "Invalid request"
            }, status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"review_{housing_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(data=cached_data, status=status.HTTP_200_OK)

        reviews = Review.objects.filter(related_to_id=housing_id)

        if not reviews.exists():
            return Response({
                "message": "No reviews found.",
            }, status=status.HTTP_404_NOT_FOUND)

        paginator = ReviewPagination()
        paginated_reviews = paginator.paginate_queryset(reviews.order_by('-review_date'), request)

        serializer = ReviewRetrieveSerializer(paginated_reviews, many=True).data
        pagination_request = paginator.get_paginated_response(serializer)

        cache.set(cache_key, pagination_request.data, timeout=600)

        return pagination_request


class AddHousingView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Response("Successful Response", HousingSerializer)},
    )
    def post(self, request):
        serializer = AddHousingSerializer(data=request.data, context={"request": request})
        print(request.data)
        if serializer.is_valid():
            housing = serializer.save(owner=request.user)

            return Response(
                {
                    "message": "Housing added.",
                }, status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class HousingDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        reviews = Prefetch("reviews", queryset=Review.objects.order_by("-review_date")[:3], to_attr="housing_reviews")
        housing = get_object_or_404(Housing.objects.prefetch_related('photos', reviews).annotate(review_amount=Count("reviews")), pk=pk)
        cache_key = f"housing_{housing.id}"

        if cache.get(cache_key):
            return Response(data=cache.get(cache_key), status=status.HTTP_200_OK)

        serializer = HousingDetailsSerializer(housing)

        cache.set(cache_key, serializer.data, timeout=600)

        return Response(serializer.data, status=status.HTTP_200_OK)

