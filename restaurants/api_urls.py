from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet  # add more ViewSets here if you have them

router = DefaultRouter()
router.register(r"restaurants", RestaurantViewSet, basename="restaurant")


urlpatterns = [
    path("", include(router.urls)),
]
