from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RestaurantViewSet,
    PublicRestaurantListView,
    PublicRestaurantDetailView,
)

# API router for backend endpoints
router = DefaultRouter()
router.register(r"restaurants", RestaurantViewSet, basename="restaurant")

# Combined URL patterns
urlpatterns = [
    # Public browsing pages (for all users)
    path("browse/", PublicRestaurantListView.as_view(), name="restaurant_browse"),
    path("<int:pk>/", PublicRestaurantDetailView.as_view(), name="restaurant_detail"),

    # API endpoints (for developers / internal use)
    path("api/", include(router.urls)),
]
