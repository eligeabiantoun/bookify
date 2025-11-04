from django.urls import path
from . import views

urlpatterns = [
    path("browse/", views.browse_restaurants, name="browse"),
    path("reserve/<int:pk>/", views.reserve_view, name="reserve"),
]
