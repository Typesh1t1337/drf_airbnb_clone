from django.urls import path
from .views import RetrieveAllHousingView, FavoritesView,WriteReviewView

urlpatterns = [
    path("housing/list/", RetrieveAllHousingView.as_view()),
    path("favorites/", FavoritesView.as_view()),
    path("review/add/", WriteReviewView.as_view()),
]