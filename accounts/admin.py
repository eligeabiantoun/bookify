from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, StaffInvitation
from restaurants.models import Restaurant  # ✅ import the real Restaurant model


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User

    # what you see in the users list
    list_display = ("email", "role", "is_email_verified", "is_staff", "is_superuser")
    list_filter = ("role", "is_email_verified", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    # hide the username field since you authenticate with email
    exclude = ("username",)

    # edit view layout
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Bookify"), {"fields": ("role", "is_email_verified")}),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # add user form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_superuser", "is_email_verified"),
        }),
    )


@admin.register(StaffInvitation)
class StaffInvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "restaurant", "role", "invited_by", "expires_at", "accepted_at", "created_at")
    list_filter = ("role", "restaurant", "accepted_at", "expires_at", "created_at")
    search_fields = ("email", "token", "invited_by__email", "restaurant__name")
    readonly_fields = ("token", "created_at")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name",)  # tweak if your Restaurant has more fields (e.g., "owner", "cuisine")
    search_fields = ("name",)
