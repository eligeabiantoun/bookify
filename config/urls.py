from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

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

    # ---------- Auth (custom views) ----------
    path("signup/", a.signup_view, name="signup"),
    path("login/", a.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),  # built-in logout
    path("verify-email/", a.verify_email_view, name="verify_email"),
    path("post-login/", a.post_login_router, name="post_login"),

    # ---------- Support / static pages ----------
    path("support/", a.contact_support, name="contact_support"),
    path("contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),

    # ---------- Password reset flow ----------
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
        name="password_reset_complete",
    ),

    # ---------- Invitations ----------
    path("auth/invitations/create/", a.create_invitation_view, name="create_invitation"),
    path("accept-invite/", a.accept_invite_view, name="accept_invite"),

    # ---------- Dashboards ----------
    path("dashboard/customer/", a.customer_dashboard, name="customer_dashboard"),
    path(
        "dashboard/customer/reservations/<int:pk>/cancel/",
        a.cancel_reservation,
        name="cancel_reservation",
        ),

    path("dashboard/owner/", a.owner_dashboard, name="owner_dashboard"),
    path("dashboard/staff/", a.staff_dashboard, name="staff_dashboard"),
    path("owner/reservations/<int:pk>/confirm/", a.owner_confirm_reservation, name="owner_confirm_reservation"),
    path("owner/reservations/<int:pk>/decline/", a.owner_decline_reservation, name="owner_decline_reservation"),


    # ---------- Built-in Django auth routes ----------
    path("accounts/", include("django.contrib.auth.urls")),

    # ---------- Restaurants ----------
    # Public browse + detail (guest pages)
    path("restaurants/", PublicRestaurantListView.as_view(), name="restaurant_browse"),
    path("restaurants/<int:pk>/", PublicRestaurantDetailView.as_view(), name="restaurant_detail"),

    # Owners manage their restaurant
    path("owner/restaurant/new/", owner_restaurant_create, name="owner_restaurant_create"),
    path("owner/restaurant/edit/", owner_restaurant_edit, name="owner_restaurant_edit"),

    # API 
    path("api/", include("restaurants.api_urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)