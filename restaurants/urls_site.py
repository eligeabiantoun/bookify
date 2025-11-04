from django.urls import path
from .views import owner_restaurant_create, owner_restaurant_edit

urlpatterns = [
    path("owner/restaurant/new/", owner_restaurant_create, name="owner_restaurant_create"),
    path("owner/restaurant/edit/", owner_restaurant_edit, name="owner_restaurant_edit"),
]
