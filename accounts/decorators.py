from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

def owner_required(view_func):
    # Robust: tolerate "Owner"/"owner" and missing field
    return user_passes_test(
        lambda u: u.is_authenticated and getattr(u, "role", "").lower() == "owner",
        login_url=getattr(settings, "LOGIN_URL", "/login/"),
    )(view_func)
