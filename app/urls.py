from django.urls import path
from .views import RetrieveAllHousingView

urlpatterns = [
    path("housing/list/", RetrieveAllHousingView.as_view())
]