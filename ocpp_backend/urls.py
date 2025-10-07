from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.contrib import admin
from django.urls import include, path

from chargers.api import views as charger_views
from chargers.api.urls import urlpatterns as charger_urls


schema_view = get_schema_view(
    openapi.Info(
        title="OCPP Backend API",
        default_version="v1",
        description="API for managing OCPP chargers and transactions",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("chargers.api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("metrics/", include("django_prometheus.urls")),  # <-- monitoring
    path("dashboard/", charger_views.dashboard, name="dashboard"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("openapi.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]
urlpatterns += charger_urls
