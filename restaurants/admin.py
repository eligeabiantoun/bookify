from django.contrib import admin

from .models import Reservation, Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "cuisine", "capacity", "rating", "owner")
    search_fields = ("name", "cuisine", "address")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "restaurant",
        "customer",
        "reservation_date",
        "reservation_time",
        "party_size",
        "status",
    )
    list_filter = ("status", "reservation_date")
    search_fields = ("restaurant__name", "customer__email", "customer__first_name", "customer__last_name")
