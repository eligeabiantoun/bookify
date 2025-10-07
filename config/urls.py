from django.contrib import admin
from django.urls import path
from accounts import views as a

urlpatterns = [
    path("admin/", admin.site.urls),

    path("signup", a.signup_view, name="signup"),
    path("login", a.login_view, name="login"),
    path("logout", a.logout_view, name="logout"),
    path("verify-email", a.verify_email_view, name="verify_email"),
    path("post-login", a.post_login_router, name="post_login"),

    path("auth/invitations/create", a.create_invitation_view, name="create_invitation"),
    path("accept-invite", a.accept_invite_view, name="accept_invite"),

    path("dashboard/customer", a.customer_dashboard, name="customer_dashboard"),
    path("dashboard/owner", a.owner_dashboard, name="owner_dashboard"),
    path("dashboard/staff", a.staff_dashboard, name="staff_dashboard"),
]
