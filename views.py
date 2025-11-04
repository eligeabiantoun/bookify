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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.decorators import owner_required  # requires accounts/decorators.py from earlier step
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


def browse_restaurants(request):
    """
    Public browse page so guests can explore restaurants without signing up.
    Provides basic search/filter controls in the template.
    """
    query = (request.GET.get("q") or "").strip()
    cuisine_filter = (request.GET.get("cuisine") or "").strip()
    sort = (request.GET.get("sort") or "rating").lower()

    restaurants = Restaurant.objects.all()

    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query)
            | Q(cuisine__icontains=query)
            | Q(address__icontains=query)
        )

    if cuisine_filter:
        restaurants = restaurants.filter(cuisine__iexact=cuisine_filter)

    sort_map = {
        "rating": ("-rating", "name"),
        "name": ("name",),
        "newest": ("-id",),
    }
    restaurants = restaurants.order_by(*sort_map.get(sort, ("-rating", "name")))

    cuisines = (
        Restaurant.objects.order_by("cuisine")
        .values_list("cuisine", flat=True)
        .distinct()
    )

    return render(
        request,
        "restaurants/browse.html",
        {
            "restaurants": restaurants,
            "query": query,
            "cuisines": cuisines,
            "active_cuisine": cuisine_filter,
            "active_sort": sort if sort in sort_map else "rating",
        },
    )


def reserve_view(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    return render(request, "reserve_placeholder.html", {"restaurant": restaurant})
