from django.urls import path
from .views import (RetrieveAllHousingView, FavoritesView,
                    WriteReviewView, HousingDetailView,
                    RetrieveReviewView, AddHousingView, UserHousingsView,
                    HousingBookView, UserBookingsView
                    )

urlpatterns = [
    path("housing/list/", RetrieveAllHousingView.as_view()),
    path("favorites/", FavoritesView.as_view()),
    path("review/add/", WriteReviewView.as_view()),
    path("review/list/", RetrieveReviewView.as_view()),
    path("housing/add/", AddHousingView .as_view()),
    path("housing/detail/<int:pk>/", HousingDetailView.as_view()),
    path("housing/user/<str:username>/", UserHousingsView.as_view()),
    path("booking/book/", HousingBookView.as_view()),
    path("booking/list/", UserBookingsView.as_view())
]