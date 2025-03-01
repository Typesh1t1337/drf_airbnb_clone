from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from app.models import Housing
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
    order_by = ["-created_at"]
    serializer_class = HousingSerializer
    filterset_class = HousingFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Housing.objects.all().exclude(owner=user)

        return Housing.objects.all()
