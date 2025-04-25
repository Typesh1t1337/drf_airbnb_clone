from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
import django_prometheus.exports as prometheus_exports

schema_view = get_schema_view(
    openapi.Info(
        title="Airbnb API",
        default_version='v1',
        description="API for Airbnb",
        contact=openapi.Contact(email="arnurzhhaill@gmail.com"),
        license=openapi.License(name="BSD License"),
        terms_of_service="https://www.google.com/policies/terms/",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("auth/api/", include("account.urls")),
    path("api/v1/", include("app.urls")),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name='schema-redoc'),
    path("metrics/", prometheus_exports.ExportToDjangoView, name='metrics'),
]
