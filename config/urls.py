from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts import views as a

urlpatterns = [
    # Home
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    # Admin
    path("admin/", admin.site.urls),

    # Auth (custom views)
    path("signup/", a.signup_view, name="signup"),
    path("login/", a.login_view, name="login"),
    path("logout/", a.logout_view, name="logout"),
    path("verify-email/", a.verify_email_view, name="verify_email"),
    path("post-login/", a.post_login_router, name="post_login"),

    # Support / static pages
    path("support/", a.contact_support, name="contact_support"),
    path("contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),

    # Password reset flow (Django auth views)
    path(
        "password-reset/",
        a.auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        a.auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        a.auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        a.auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
        name="password_reset_complete",
    ),

    # Invitations
    path("auth/invitations/create/", a.create_invitation_view, name="create_invitation"),
    path("accept-invite/", a.accept_invite_view, name="accept_invite"),

    # Dashboards
    path("dashboard/customer/", a.customer_dashboard, name="customer_dashboard"),
    path("dashboard/customer/reservations/<int:pk>/cancel/", a.cancel_reservation, name="customer_cancel_reservation"),
    path("dashboard/owner/", a.owner_dashboard, name="owner_dashboard"),
    path("dashboard/staff/", a.staff_dashboard, name="staff_dashboard"),

    # Built-in auth URLs (login/logout/password change, etc.)
    path("accounts/", include("django.contrib.auth.urls")),

    # ---------- Restaurants ----------
    # Public site pages (e.g., /browse/, /<id>/) — keep browse inside restaurants app
    path("", include("restaurants.urls_site")),

    # Owner/staff site pages under /restaurants/ (non-API pages)
    path("restaurants/", include("restaurants.urls")),

    # API mounted once at /api/ (ensure you created restaurants/api_urls.py with DRF router)
    path("api/", include("restaurants.api_urls")),
]
