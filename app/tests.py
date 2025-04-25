import pytest
from django.contrib.auth import get_user_model
from .models import Housing, TypeOfHousing, Review, Booking, Favorites

User = get_user_model()

@pytest.mark.django_db
def test_create_type_of_housing():
    t = TypeOfHousing.objects.create(name="Apartment")
    assert t.name == "Apartment"

@pytest.mark.django_db
def test_create_housing():
    user = User.objects.create_user(username="testuser", password="testpass")
    housing_type = TypeOfHousing.objects.create(name="Villa")
    housing = Housing.objects.create(
        name="Cozy Villa",
        owner=user,
        description="A nice place",
        address="123 Street",
        city="NiceCity",
        country="Dreamland",
        rated_people=3,
        rating_amount=4.5,
        price=100,
        option="Per day",
        type=housing_type,
        conveniences="WiFi, Pool"
    )
    assert housing.owner == user
    assert housing.type == housing_type
    assert housing.price == 100

@pytest.mark.django_db
def test_create_review():
    user = User.objects.create_user(username="reviewer", password="pass")
    housing_type = TypeOfHousing.objects.create(name="Cabin")
    housing = Housing.objects.create(
        name="Forest Cabin",
        owner=user,
        description="Secluded and peaceful",
        address="Nowhere",
        city="SilentHill",
        country="NowhereLand",
        rated_people=0,
        rating_amount=0,
        price=80,
        option="Per day",
        type=housing_type,
        conveniences="Fireplace"
    )
    review = Review.objects.create(
        review_owner=user,
        review_text="Great stay!",
        review_rating=5,
        related_to=housing
    )
    assert review.related_to == housing
    assert review.review_rating == 5

@pytest.mark.django_db
def test_favorites_model():
    user = User.objects.create_user(username="favuser", password="pass")
    housing_type = TypeOfHousing.objects.create(name="Tent")
    housing = Housing.objects.create(
        name="Camping Tent",
        owner=user,
        description="Outdoorsy",
        address="Nature Road",
        city="Greenland",
        country="Wild",
        rated_people=0,
        rating_amount=0,
        price=10,
        option="Per day",
        type=housing_type,
        conveniences="Nature"
    )
    fav = Favorites.objects.create(
        favorites_owner=user,
        favorites_housing=housing
    )
    assert fav.favorites_housing == housing

@pytest.mark.django_db
def test_booking_model():
    user = User.objects.create_user(username="booker", password="pass")
    housing_type = TypeOfHousing.objects.create(name="House")
    housing = Housing.objects.create(
        name="Big House",
        owner=user,
        description="Spacious",
        address="Main Blvd",
        city="Metrocity",
        country="Utopia",
        rated_people=0,
        rating_amount=0,
        price=200,
        option="Per day",
        type=housing_type,
        conveniences="Garage"
    )
    booking = Booking.objects.create(
        owner=user,
        housing=housing,
        check_in_date="2025-05-01",
        check_out_date="2025-05-07"
    )
    assert booking.owner == user
    assert booking.housing == housing
