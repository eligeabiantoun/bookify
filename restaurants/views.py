# restaurants/views.py

# ---------- API (DRF) ----------
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Restaurant
from .serializers import RestaurantSerializer
from .permissions import IsOwnerOrReadOnly

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


# ---------- Site views (HTML pages for owners) ----------
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.decorators import owner_required
from .forms import RestaurantForm


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


# ---------- Public browse & detail views (PUBLIC for guests AND logged-in users) ----------
from django.views.generic import ListView, DetailView

class PublicRestaurantListView(ListView):
    """
    Public list view: anyone can browse restaurants (even if logged in).
    Booking is handled elsewhere and requires login.
    """
    template_name = "restaurants/browse.html"
    model = Restaurant
    context_object_name = "restaurants"
    paginate_by = 12

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
    """
    Public detail page: anyone can view restaurant details.
    Templates show 'Log in to book' for guests; logged-in users can also view it.
    """
    template_name = "restaurants/detail.html"
    model = Restaurant
    context_object_name = "restaurant"
