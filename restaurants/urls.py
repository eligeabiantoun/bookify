# restaurants/urls.py
from django.urls import path
from .views import (
    PublicRestaurantListView,
    PublicRestaurantDetailView,
)

# These are normal site URLs (non-API)
urlpatterns = [
    path("browse/", PublicRestaurantListView.as_view(), name="restaurant_browse"),
    path("<int:pk>/", PublicRestaurantDetailView.as_view(), name="restaurant_detail"),
]
