from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, StaffInvitation, Restaurant

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("email","role","is_email_verified","is_staff","is_superuser")
    fieldsets = (
        (None, {"fields": ("email","password","role","is_email_verified")}),
        ("Personal info", {"fields": ("first_name","last_name")}),
        ("Permissions", {"fields": ("is_active","is_staff","is_superuser","groups","user_permissions")}),
        ("Important dates", {"fields": ("last_login","date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email","password1","password2","role")}),)
    search_fields = ("email",)
    ordering = ("email",)

admin.site.register(StaffInvitation)
admin.site.register(Restaurant)
