import datetime
import json

from django import forms
from django.utils import timezone

from .models import Reservation, Restaurant


# -------------------------------
# Restaurant (owner form)
# -------------------------------
class RestaurantForm(forms.ModelForm):
    opening_hours = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "opening-hours-input"}),
    )

    class Meta:
        model = Restaurant
        fields = [
            "name",
            "address",
            "cuisine",
            "capacity",
            "description",
            "opening_hours",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing = self.initial.get("opening_hours")
        if isinstance(existing, dict):
            existing = json.dumps(existing, separators=(",", ":"))
        if not existing and getattr(self.instance, "opening_hours", None):
            existing = json.dumps(self.instance.opening_hours, separators=(",", ":"))
        if existing:
            self.initial["opening_hours"] = existing
            self.fields["opening_hours"].initial = existing

    def clean_opening_hours(self):
        data = (self.cleaned_data.get("opening_hours") or "").strip()
        if not data:
            return {}
        try:
            parsed = json.loads(data)
            if not isinstance(parsed, dict):
                raise ValueError
            return parsed
        except Exception:
            raise forms.ValidationError(
                "opening_hours must be valid JSON (e.g. {'Mon': {'open':'09:00','close':'22:00'}})"
            )


# -------------------------------
# Reservation (customer request)
# -------------------------------
class ReservationForm(forms.ModelForm):
    # Use text inputs with classes so Flatpickr (or native) can attach.
    reservation_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "input datepicker"})
    )
    reservation_time = forms.TimeField(
        widget=forms.TimeInput(attrs={"class": "input timepicker"})
    )

    class Meta:
        model = Reservation
        fields = ["restaurant", "reservation_date", "reservation_time", "party_size", "notes"]
        widgets = {
            "restaurant": forms.HiddenInput(),
            "party_size": forms.NumberInput(attrs={"class": "input", "min": 1}),
            "notes": forms.Textarea(
                attrs={"class": "input textarea", "rows": 3, "placeholder": "Optional notes for the restaurant"}
            ),
        }

    def __init__(self, *args, **kwargs):
        restaurant_queryset = kwargs.pop("restaurant_queryset", None)
        super().__init__(*args, **kwargs)
        queryset = restaurant_queryset or Restaurant.objects.all()
        self.fields["restaurant"].queryset = queryset

    def clean_party_size(self):
        size = self.cleaned_data.get("party_size")
        if not size or size < 1:
            raise forms.ValidationError("Party size must be at least 1 guest.")
        return size

    def clean(self):
        cleaned = super().clean()
        restaurant = cleaned.get("restaurant")
        reservation_date = cleaned.get("reservation_date")
        reservation_time = cleaned.get("reservation_time")
        party_size = cleaned.get("party_size")

        if restaurant and party_size and party_size > restaurant.capacity:
            self.add_error("party_size", f"Maximum party size is {restaurant.capacity} seats.")

        if reservation_date and reservation_time:
            combined = datetime.datetime.combine(reservation_date, reservation_time)
            tz = timezone.get_current_timezone()
            aware_combined = timezone.make_aware(combined, tz)
            if aware_combined < timezone.now():
                msg = "Please choose a future date and time."
                self.add_error("reservation_date", msg)
                self.add_error("reservation_time", msg)

        return cleaned
