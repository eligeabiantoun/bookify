# restaurants/views.py

# ---------- stdlib ----------
import datetime

# ---------- Django / DRF imports ----------
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# ---------- Local imports ----------
from .models import Restaurant, Reservation
from .serializers import RestaurantSerializer
from .permissions import IsOwnerOrReadOnly
from .forms import RestaurantForm
from accounts.decorators import owner_required


# ---------- API (DRF) ----------
class RestaurantViewSet(viewsets.ModelViewSet):
    """
    REST API for restaurants.
    - Authenticated users can create/update/delete their own restaurants.
    - Everyone can read.
    - Supports ?search= and ?ordering=.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "cuisine", "address"]
    ordering_fields = ["rating", "capacity", "name"]
    ordering = ["-rating"]

    def perform_create(self, serializer):
        # Attach the logged-in user as owner on create
        serializer.save(owner=self.request.user)


# ---------- Owner site views (HTML pages) ----------
@login_required
@owner_required
def owner_restaurant_create(request):
    """
    Owner creates their restaurant from the website (not admin).
    If the owner already has one, redirect to edit page.
    """
    existing = Restaurant.objects.filter(owner=request.user).first()
    if existing:
        return redirect("owner_restaurant_edit")

    if request.method == "POST":
        form = RestaurantForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.owner = request.user
            r.save()
            messages.success(request, "Restaurant created.")
            return redirect("owner_restaurant_edit")
    else:
        form = RestaurantForm()

    return render(
        request,
        "restaurants/owner_restaurant_form.html",
        {"form": form, "mode": "create"},
    )


@login_required
@owner_required
def owner_restaurant_edit(request):
    """
    Owner edits their existing restaurant.
    Assumes one restaurant per owner.
    """
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if restaurant is None:
        messages.info(request, "Create your restaurant to start managing it.")
        return redirect("owner_restaurant_create")

    if request.method == "POST":
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Restaurant updated.")
            return redirect("owner_restaurant_edit")
    else:
        form = RestaurantForm(instance=restaurant)

    return render(
        request,
        "restaurants/owner_restaurant_form.html",
        {"form": form, "mode": "edit"},
    )


# ---------- Public browse & detail views ----------
# NOTE: Browse is guest-only by policy; if a user is logged in, we log them out here.
class PublicRestaurantListView(ListView):
    """
    Guest browse list:
    - If a user is logged in, they are immediately logged out
      and continue browsing as an anonymous (guest) visitor.
    """
    template_name = "restaurants/browse.html"
    model = Restaurant
    context_object_name = "restaurants"
    paginate_by = 12

    # def dispatch(self, request, *args, **kwargs):
    #     # Force any authenticated user to be logged out
    #     if request.user.is_authenticated:
    #         logout(request)
    #     return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Restaurant.objects.all().order_by("name")
        q = self.request.GET.get("q", "").strip()
        cuisine = self.request.GET.get("cuisine", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(address__icontains=q))
        if cuisine:
            qs = qs.filter(cuisine__icontains=cuisine)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        ctx["cuisine"] = self.request.GET.get("cuisine", "").strip()
        return ctx


class PublicRestaurantDetailView(DetailView):
    template_name = "restaurants/detail.html"
    model = Restaurant
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        r = self.object

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        full_names = {
            "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
            "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday",
        }

        rows = []
        oh = getattr(r, "opening_hours", None)

        if isinstance(oh, dict):
            def pick_day(d3):
                # Try multiple key variants to match your JSON
                candidates = [
                    d3, d3.lower(), d3.upper(), d3.title(),
                    full_names[d3], full_names[d3].lower(), full_names[d3].upper(), full_names[d3].title(),
                ]
                for k in candidates:
                    v = oh.get(k)
                    if v:
                        return v
                return None

            for d in days:
                v = pick_day(d) or {}
                # Support common key variants
                o = v.get("open") or v.get("Open") or v.get("start") or v.get("from")
                c = v.get("close") or v.get("Close") or v.get("end") or v.get("to")
                rows.append((d, o, c))
        else:
            # Fallback to single opening_time / closing_time fields
            ot = getattr(r, "opening_time", None)
            ct = getattr(r, "closing_time", None)

            def fmt(t):
                try:
                    return t.strftime("%H:%M") if t else None
                except Exception:
                    return t  # if already a string

            for d in days:
                rows.append((d, fmt(ot), fmt(ct)))

        ctx["opening_rows"] = rows
        return ctx


# ---------- Customer reservation actions ----------
@login_required
@require_POST
def cancel_reservation(request, pk):
    """
    Allow a logged-in customer to cancel their own reservation
    if it is pending or confirmed.
    """
    reservation = get_object_or_404(
        Reservation,
        pk=pk,
        customer=request.user,
    )

    if reservation.status not in ("pending", "confirmed"):
        messages.error(request, "This reservation cannot be cancelled.")
        # Change "customer_dashboard" if your dashboard URL name is different.
        return redirect("customer_dashboard")

    reservation.status = "cancelled"
    reservation.save()

    messages.success(request, "Your reservation has been cancelled.")
    # Change "customer_dashboard" if your dashboard URL name is different.
    return redirect("customer_dashboard")
