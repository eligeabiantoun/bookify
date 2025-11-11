from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from accounts import views as a
from restaurants.views import (
    PublicRestaurantListView,
    PublicRestaurantDetailView,
    owner_restaurant_create,
    owner_restaurant_edit,
)

urlpatterns = [
    # ---------- Home ----------
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    # ---------- Admin ----------
    path("admin/", admin.site.urls),

    # ---------- Auth ----------
    path("signup/", a.signup_view, name="signup"),
    path("login/", a.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("verify-email/", a.verify_email_view, name="verify_email"),
    path("post-login/", a.post_login_router, name="post_login"),

    # ---------- Accounts (built-in auth URLs) ----------
    path("accounts/", include("django.contrib.auth.urls")),

    # ---------- Restaurants ----------
    path("restaurants/", PublicRestaurantListView.as_view(), name="restaurant_browse"),
    path("restaurants/<int:pk>/", PublicRestaurantDetailView.as_view(), name="restaurant_detail"),
    path("owner/restaurant/new/", owner_restaurant_create, name="owner_restaurant_create"),
    path("owner/restaurant/edit/", owner_restaurant_edit, name="owner_restaurant_edit"),

    # ---------- API (optional) ----------
    path("api/", include("restaurants.api_urls")),
]
