from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="restaurants",
    )
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    cuisine = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    opening_hours = models.JSONField(blank=True, default=dict)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        DECLINED = "DECLINED", "Declined"

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    party_size = models.PositiveIntegerField()
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["reservation_date", "reservation_time"]

    def __str__(self):
        return f"{self.customer} -> {self.restaurant} @ {self.reservation_date} {self.reservation_time}"
