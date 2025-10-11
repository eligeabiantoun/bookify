from django.contrib import admin
from django.urls import path, include
from accounts import views as a
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    path("admin/", admin.site.urls),

    path("signup/", a.signup_view, name="signup"),
    path("login/", a.login_view, name="login"),
    path("logout/", a.logout_view, name="logout"),
    path("verify-email/", a.verify_email_view, name="verify_email"),
    path("post-login/", a.post_login_router, name="post_login"),

    # Support link target stays the same
    path("support/", a.contact_support, name="contact_support"),

    path("browse/", TemplateView.as_view(template_name="browse.html"), name="browse"),

    # ✅ Only change: give this a different name to avoid clashing
    path("contact/", TemplateView.as_view(template_name="contact.html"), name="contact"),

    # password reset flow
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    path("auth/invitations/create/", a.create_invitation_view, name="create_invitation"),
    path("accept-invite/", a.accept_invite_view, name="accept_invite"),

    path("dashboard/customer/", a.customer_dashboard, name="customer_dashboard"),
    path("dashboard/owner/", a.owner_dashboard, name="owner_dashboard"),
    path("dashboard/staff/", a.staff_dashboard, name="staff_dashboard"),

    # Built-in auth extras
    path("accounts/", include("django.contrib.auth.urls")),
]
