from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import OuterRef, Subquery, Exists, Count, Prefetch, When, Value, Case, IntegerField
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
from .tasks import book_notification_email, email_finished_notification
from .serializer import *
from account.permissions import IsNotBanned


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
        ).order_by("-created_at").exclude(status=False)

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
    permission_classes = [IsAuthenticated, IsNotBanned]

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
    permission_classes = [IsAuthenticated, IsNotBanned]

    def post(self, request):
        user = request.user
        serializer = ReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        housing_id = serializer.validated_data['housing_id']
        rating = serializer.validated_data['rating']
        text = serializer.validated_data['text']

        housing_obj = get_object_or_404(Housing, pk=housing_id)

        try:
            booking = Booking.objects.get(housing_id=housing_id, owner=user, status="Finished")
        except Booking.DoesNotExist:
            return Response(
                {"message": "You don't have any bookings for this housing."},
                status=status.HTTP_404_NOT_FOUND
            )

        if Review.objects.filter(related_to=housing_obj, review_owner=user).exists():
            return Response(
                {"message": "You have already added a review."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Review.objects.create(
            related_to=housing_obj,
            review_owner=user,
            review_text=text,
            review_rating=rating
        )

        housing_obj.rated_people = (housing_obj.rated_people or 0) + 1
        housing_obj.rating_amount = (housing_obj.rating_amount or 0) + rating
        housing_obj.save(update_fields=["rating_amount", "rated_people"])

        booking.status = "Reviewed"
        booking.save(update_fields=["status"])

        cache.delete(f"review_{housing_id}")
        cache.delete(f"user_bookings_{user.username}")

        return Response(
            {"message": "Review successfully added."},
            status=status.HTTP_201_CREATED
        )


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

        reviews = Review.objects.filter(related_to_id=housing_id).select_related("review_owner").order_by("-review_date")

        if not reviews.exists():
            return Response({
                "message": "No reviews found.",
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewRetrieveSerializer(reviews, many=True).data

        cache.set(cache_key, serializer, timeout=600)

        return Response(serializer, status=status.HTTP_200_OK)


class AddHousingView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    @swagger_auto_schema(
        responses={200: openapi.Response("Successful Response", HousingSerializer)},
    )
    def post(self, request):
        user = request.user
        serializer = AddHousingSerializer(data=request.data, context={"request": request})
        cache_key = f"housings_{user.username}"

        if serializer.is_valid():
            housing = serializer.save(owner=request.user)

            return Response(
                {
                    "housing_id": housing.id,
                }, status=status.HTTP_201_CREATED
            )

        if cache.get(cache_key):
            cache.delete(cache_key)

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class HousingDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        reviews = Prefetch("reviews", queryset=Review.objects.order_by("-review_date")[:3], to_attr="housing_reviews")
        housing = get_object_or_404(Housing.objects.prefetch_related('photos', reviews).select_related("owner").annotate(review_amount=Count("reviews")), pk=pk)
        cache_key = f"housing_{housing.id}"

        if cache.get(cache_key):
            return Response(data=cache.get(cache_key), status=status.HTTP_200_OK)

        serializer = HousingDetailsSerializer(housing)

        cache.set(cache_key, serializer.data, 600)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserHousingsView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def get(self, request, username):
        user = get_object_or_404(get_user_model(), username=username)
        cache_key = f"housings_{username}"

        if cache.get(cache_key):
            return Response(cache.get(cache_key), status=status.HTTP_200_OK)

        wallpaper = HousingPhotos.objects.filter(is_wallpaper=True)
        my_housings = (Housing.objects.
                       filter(owner=user).
                       select_related("type").
                       prefetch_related(Prefetch("photos", queryset=wallpaper, to_attr="wallpaper_photo")))

        serializer = UserHousingsSerializer(my_housings, many=True).data

        cache.set(cache_key, serializer, 600)

        return Response(serializer, status=status.HTTP_200_OK)


class HousingBookView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def post(self, request):
        user = request.user

        serializer = HousingBookSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        housing_id = serializer.validated_data["housing_id"]
        check_in = serializer.validated_data["check_in"]
        check_out = serializer.validated_data["check_out"]
        bill = serializer.validated_data["bill"]

        overlapping = Booking.objects.filter(owner=user, housing_id=housing_id, check_in_date__lt=check_out, check_out_date__gt=check_in).exists()

        if overlapping:
            return Response(
                {
                    "message": "Housing booking already taken.",
                }, status=status.HTTP_400_BAD_REQUEST
            )

        booking = Booking.objects.create(owner=user, housing_id=housing_id, check_in_date=check_in, check_out_date=check_out, bill_to_pay=bill)

        cache_key = f"user_bookings_{user.username}"

        book_notification_email.delay(user_id=user.id, booking_id=booking.id)

        if cache.get(cache_key):
            cache.delete(cache_key)

        return Response({
            "message": "Housing booking successful.",
        }, status=status.HTTP_200_OK)


class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def get(self, request):
        user = request.user

        cache_key = f"user_bookings_{user.username}"

        if cache.get(cache_key):
            return Response(cache.get(cache_key), status=status.HTTP_200_OK)

        bookings = (Booking.objects.filter(owner=user).exclude(status="reviewed")
                    .select_related("housing")
                    .prefetch_related(
                    Prefetch("housing__photos", queryset=HousingPhotos.objects.filter(is_wallpaper=True), to_attr="wallpaper"))
                    )

        serializer = UserBookingSerializer(bookings, many=True).data
        cache.set(cache_key, serializer, 600)

        return Response(serializer, status=status.HTTP_200_OK)


class RemoveBookingView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def delete(self, request, pk):
        user = request.user
        cache_key = f"user_bookings_{user.username}"

        try:
            booking = Booking.objects.get(id=pk, owner=user)
        except Booking.DoesNotExist:
            return Response({
                "message": "Booking does not exist.",
            }, status=status.HTTP_404_NOT_FOUND)

        booking.delete()
        cache.delete(cache_key)

        return Response({"message": "Booking removed."}, status=status.HTTP_200_OK)


class MyHousingReservationsView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def get(self, request):
        user = request.user
        cache_key = f"my_housing_reservations_{user.username}"

        if cache.get(cache_key):
            return Response(cache.get(cache_key), status=status.HTTP_200_OK)

        bookings = (Booking.objects.filter(housing__owner=user).
                    select_related("owner", "housing").
                    annotate(status_order=Case(
                When(status="Booked", then=Value(1)),
                        When(status="Finished", then=Value(2)),
                        When(status="Reviewed", then=Value(3)),
                        output_field=IntegerField()
                    )).
                    order_by("-created_at"))

        serializer = MyHousingReservationSerializer(bookings, many=True)

        cache.set(cache_key, serializer.data, 30)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ConfirmCheckingOutView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def patch(self, request, pk):
        user = request.user
        cache_key = f"my_housing_reservations_{user.username}"

        booking = get_object_or_404(Booking, id=pk, housing__owner=user)

        current_time = date.today()
        if current_time < booking.check_out_date:
            return Response({
                "message": "Guests are not checking out yet.",
            }, status=status.HTTP_400_BAD_REQUEST)

        booking.status = "Finished"
        booking.save()
        email_finished_notification.delay(user_id=booking.owner.id, booking_id=booking.id)

        if cache.get(cache_key):
            cache.delete(cache_key)
            cache.delete(f"user_bookings_{booking.owner.username}")

        return Response({"message": "Checking out successful."}, status=status.HTTP_200_OK)
