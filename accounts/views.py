import datetime
from urllib.parse import urlparse  # ✅ ADDED

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, resolve  # ✅ ADDED resolve
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.http import url_has_allowed_host_and_scheme  # ✅ ADDED
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignupForm
from .models import StaffInvitation, User
from restaurants.forms import ReservationForm
from restaurants.models import Reservation, Restaurant


def _send_verification_email(user, request):
    token = user.make_email_token()
    link = request.build_absolute_uri(reverse("verify_email") + f"?token={token}")
    send_mail(
        subject="Verify your Bookify email",
        message=f"Click to verify your account: {link}",
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        recipient_list=[user.email],
    )


def signup_view(request):
    if request.method == "POST":
        if request.POST.get("role") == User.Roles.STAFF:
            messages.error(
                request,
                "Staff accounts are invite-only. Ask your manager for an invite link.",
            )
            return redirect("signup")
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                role=form.cleaned_data["role"],
            )
            _send_verification_email(user, request)
            return render(
                request,
                "accounts/verify_prompt.html",
                {"email": user.email},
            )
        else:
            return render(
                request,
                "accounts/signup.html",
                {"form": form},
                status=400,
            )
    form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    """
    Login with safe redirect:
    - Honors ?next= only if it's safe AND matches the user's role when it points to a dashboard
    - Otherwise routes by role via post_login_router
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is None:
                messages.error(request, "Invalid credentials.")
            else:
                if not user.is_email_verified:
                    return render(
                        request,
                        "accounts/verify_prompt.html",
                        {"email": user.email},
                    )

                login(request, user)

                # --- Respect and sanitize 'next', but avoid role/dashboard mismatches
                next_url = request.POST.get("next") or request.GET.get("next")

                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    path = urlparse(next_url).path
                    try:
                        target_name = resolve(path).url_name
                    except Exception:
                        target_name = None

                    # Role -> allowed dashboard
                    role_to_dash = {
                        User.Roles.CUSTOMER: "customer_dashboard",
                        User.Roles.OWNER: "owner_dashboard",
                        User.Roles.STAFF: "staff_dashboard",
                    }
                    allowed_dash = role_to_dash.get(user.role)
                    dashboard_names = {
                        "customer_dashboard",
                        "owner_dashboard",
                        "staff_dashboard",
                    }

                    # If next points to a dashboard that isn't the user's → override
                    if target_name in dashboard_names and target_name != allowed_dash:
                        return redirect(allowed_dash)

                    # Don't send logged-in users to guest/public routes
                    name_lc = (target_name or "").lower()
                    path_lc = (path or "").lower()
                    is_guestish = any(
                        k in name_lc for k in ("guest", "public", "unregistered")
                    ) or any(
                        seg in path_lc
                        for seg in ("/guest", "/public", "/unregistered")
                    )
                    if is_guestish:
                        return redirect(allowed_dash or "customer_dashboard")

                    # Otherwise honor the next URL
                    return redirect(next_url)

                # No usable/appropriate next → route by role
                return post_login_router(request)
    else:
        form = LoginForm()

    # Keep carrying ?next= to the form (your login.html has a hidden input named "next")
    return render(
        request,
        "registration/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
        },
    )


def logout_view(request):
    logout(request)
    return redirect("home")


def verify_email_view(request):
    token = request.GET.get("token")
    user = User.verify_email_token(token) if token else None
    if not user:
        return render(
            request,
            "accounts/error.html",
            {"message": "Invalid or expired verification link."},
            status=400,
        )
    user.is_email_verified = True
    user.save()
    messages.success(request, "Email verified. You can now log in.")
    return redirect("login")


@login_required
def post_login_router(request):
    role = request.user.role
    if role == User.Roles.CUSTOMER:
        return redirect("customer_dashboard")
    if role == User.Roles.OWNER:
        return redirect("owner_dashboard")
    if role == User.Roles.STAFF:
        return redirect("staff_dashboard")
    return HttpResponseForbidden("Unknown role")


def is_owner(u):
    return u.is_authenticated and u.role == User.Roles.OWNER


@login_required
@user_passes_test(is_owner)
def create_invitation_view(request):
    """Owner creates a staff invitation."""
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    if restaurant is None:
        messages.error(request, "Create your restaurant before inviting staff.")
        return redirect("owner_restaurant_create")

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        if not email:
            messages.error(request, "Email address is required.")
            return redirect("owner_dashboard")
        existing = StaffInvitation.objects.filter(
            invited_by=request.user,
            email__iexact=email,
            accepted_at__isnull=True,
            expires_at__gt=timezone.now(),
        ).first()
        if existing:
            messages.warning(
                request, f"An active invite already exists for {email}."
            )
            return redirect("owner_dashboard")
        inv = StaffInvitation.new_invite(
            email=email,
            invited_by=request.user,
            restaurant=restaurant,
        )
        link = request.build_absolute_uri(
            reverse("accept_invite") + f"?token={inv.token}"
        )
        send_mail(
            subject="Your Bookify staff invite",
            message=f"Open this link to join: {link}",
            from_email=None,
            recipient_list=[email],
        )
        messages.success(request, f"Invitation sent to {email}")
        return redirect("owner_dashboard")
    return render(request, "accounts/create_invite.html")


def accept_invite_view(request):
    """Staff accepts invitation and sets a password."""
    token = (
        request.GET.get("token")
        if request.method == "GET"
        else request.POST.get("token")
    )
    inv = StaffInvitation.objects.filter(token=token).first()
    if not inv or not inv.is_valid():
        return render(
            request,
            "accounts/error.html",
            {"message": "Invalid or expired invitation."},
            status=400,
        )
    if request.method == "POST":
        pwd = request.POST.get("password")
        if (
            pwd
            and len(pwd) >= 8
            and any(c.isalpha() for c in pwd)
            and any(c.isdigit() for c in pwd)
        ):
            user = User.objects.create_user(
                email=inv.email,
                password=pwd,
                role=User.Roles.STAFF,
                is_email_verified=True,
            )
            inv.accepted_at = timezone.now()
            inv.save()
            messages.success(request, "Account created. You can log in.")
            return redirect("login")
        messages.error(
            request,
            "Password must be at least 8 chars, with letters and digits.",
        )
    return render(
        request,
        "accounts/accept_invite.html",
        {"token": token},
    )


@login_required
def customer_dashboard(request):
    if request.user.role != User.Roles.CUSTOMER:
        return HttpResponseForbidden("403")

    search_query = (request.GET.get("q") or "").strip()

    # ---------- RESTAURANT LIST + SEARCH ----------
    restaurants_qs = Restaurant.objects.all()
    if search_query:
        restaurants_qs = restaurants_qs.filter(
            Q(name__icontains=search_query)
            | Q(cuisine__icontains=search_query)
            | Q(address__icontains=search_query)
        )
    restaurants_qs = restaurants_qs.order_by("-rating", "name")
    restaurants_list = list(restaurants_qs)

    reservation_form_with_errors = None    # a ReservationForm with errors, or None
    active_restaurant_id = None            # which card should show the errors

    # ---------- HANDLE RESERVATION POST ----------
    if request.method == "POST":
        form = ReservationForm(
            request.POST,
            restaurant_queryset=restaurants_qs,
        )
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.customer = request.user
            reservation.status = Reservation.Status.PENDING
            reservation.save()
            return redirect("customer_dashboard")
        # form invalid – keep errors attached to the right restaurant card
        reservation_form_with_errors = form
        try:
            active_restaurant_id = int(request.POST.get("restaurant"))
        except (TypeError, ValueError):
            active_restaurant_id = None

    # ---------- OPENING HOURS HELPER ----------
    def build_opening_hours_rows(raw_hours):
        rows = []
        if isinstance(raw_hours, dict):
            ordered_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            seen = set()
            for day in ordered_days:
                hours = raw_hours.get(day)
                if hours is None:
                    continue
                seen.add(day)
                if isinstance(hours, dict):
                    rows.append(
                        (day, f"{hours.get('open', '--')} - {hours.get('close', '--')}")
                    )
                else:
                    rows.append((day, str(hours)))
            # Include any extra/custom keys
            for day, hours in raw_hours.items():
                if day in seen:
                    continue
                if isinstance(hours, dict):
                    rows.append(
                        (day, f"{hours.get('open', '--')} - {hours.get('close', '--')}")
                    )
                else:
                    rows.append((day, str(hours)))
        return rows

    # ---------- BUILD RESTAURANT CARDS PAYLOAD ----------
    restaurants_payload = []
    for restaurant in restaurants_list:
        if (
            reservation_form_with_errors is not None
            and active_restaurant_id == restaurant.id
        ):
            form_instance = reservation_form_with_errors
        else:
            form_instance = ReservationForm(
                initial={"restaurant": restaurant.pk},
                restaurant_queryset=restaurants_qs,
            )

        restaurants_payload.append(
            {
                "obj": restaurant,
                "opening_hours": build_opening_hours_rows(restaurant.opening_hours),
                "form": form_instance,
            }
        )

    # ---------- CUSTOMER RESERVATIONS: UPCOMING vs PAST ----------
    tz = timezone.get_current_timezone()
    today = timezone.localdate()
    upcoming = []
    past = []

    reservations_qs = (
        Reservation.objects.filter(customer=request.user)
        .select_related("restaurant")
        .order_by("reservation_date", "reservation_time")
    )

    for reservation in reservations_qs:
        # Build a datetime purely for sorting / display; classification uses DATE only
        combined = datetime.datetime.combine(
            reservation.reservation_date, reservation.reservation_time
        )
        if timezone.is_naive(combined):
            reservation_dt = timezone.make_aware(combined, tz)
        else:
            reservation_dt = combined.astimezone(tz)

        payload = {
            "instance": reservation,
            "datetime": reservation_dt,
        }

        # ✅ Logic:
        # - If date is today or in the future AND status is not CANCELLED/DECLINED → UPCOMING
        # - Otherwise → PAST & CANCELLED
        if (
            reservation.reservation_date >= today
            and reservation.status
            not in (Reservation.Status.CANCELLED, Reservation.Status.DECLINED)
        ):
            upcoming.append(payload)
        else:
            past.append(payload)

    # newest past first
    past.sort(key=lambda item: item["datetime"], reverse=True)

    context = {
        "search_query": search_query,
        "restaurants": restaurants_payload,
        "has_restaurants": bool(restaurants_payload),
        "upcoming_reservations": upcoming,
        "past_reservations": past[:5],
        "active_restaurant_id": active_restaurant_id,
    }
    return render(request, "accounts/dashboard_customer.html", context)


@login_required
def cancel_reservation(request, pk):
    if request.user.role != User.Roles.CUSTOMER:
        return HttpResponseForbidden("403")

    reservation = get_object_or_404(
        Reservation,
        pk=pk,
        customer=request.user,
    )

    if request.method == "POST":
        if reservation.status == Reservation.Status.CANCELLED:
            messages.info(request, "This reservation was already cancelled.")
        else:
            reservation.status = Reservation.Status.CANCELLED
            reservation.save(update_fields=["status", "updated_at"])
    else:
        messages.error(request, "Invalid request.")

    return redirect("customer_dashboard")


@login_required
@require_POST
def owner_confirm_reservation(request, pk):
    if request.user.role != User.Roles.OWNER:
        return HttpResponseForbidden("403")

    reservation = get_object_or_404(
        Reservation,
        pk=pk,
        restaurant__owner=request.user,
    )

    if reservation.status == Reservation.Status.CANCELLED:
        messages.error(request, "This reservation was already cancelled.")
    else:
        reservation.status = Reservation.Status.CONFIRMED
        reservation.save(update_fields=["status", "updated_at"])

    return redirect("owner_dashboard")


@login_required
@require_POST
def owner_decline_reservation(request, pk):
    if request.user.role != User.Roles.OWNER:
        return HttpResponseForbidden("403")

    reservation = get_object_or_404(
        Reservation,
        pk=pk,
        restaurant__owner=request.user,
    )

    if reservation.status in (
        Reservation.Status.CANCELLED,
        Reservation.Status.DECLINED,
    ):
        messages.info(request, "This reservation was already cancelled/declined.")
    else:
        reservation.status = Reservation.Status.DECLINED
        reservation.save(update_fields=["status", "updated_at"])
        messages.success(request, "Reservation declined.")

    return redirect("owner_dashboard")

@login_required
def owner_dashboard(request):
    if request.user.role != User.Roles.OWNER:
        return HttpResponseForbidden("403")

    # Single restaurant for header/opening-hours display (if any)
    restaurant = Restaurant.objects.filter(owner=request.user).first()
    has_restaurant = restaurant is not None

    # --- Opening hours table (unchanged) ---
    opening_hours_rows = []
    if restaurant and isinstance(restaurant.opening_hours, dict):
        ordered_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in ordered_days:
            hours = restaurant.opening_hours.get(day)
            if isinstance(hours, dict):
                opening_hours_rows.append(
                    (day, f"{hours.get('open', '--')} - {hours.get('close', '--')}")
                )
            elif hours:
                opening_hours_rows.append((day, str(hours)))
        # include any custom keys not in the standard weekday list
        for day, hours in restaurant.opening_hours.items():
            if day in ordered_days:
                continue
            if isinstance(hours, dict):
                opening_hours_rows.append(
                    (day, f"{hours.get('open', '--')} - {hours.get('close', '--')}")
                )
            elif hours:
                opening_hours_rows.append((day, str(hours)))

    # --- Staff invites (unchanged) ---
    invites_qs = (
        StaffInvitation.objects.filter(invited_by=request.user)
        .select_related("restaurant")
        .order_by("-created_at")
    )
    now = timezone.now()
    active_invites = []
    expired_invites = []
    for invite in invites_qs:
        payload = {
            "obj": invite,
            "link": request.build_absolute_uri(
                reverse("accept_invite") + f"?token={invite.token}"
            ),
            "created_display": timesince(invite.created_at, now),
        }
        if invite.accepted_at:
            continue
        if invite.expires_at > now:
            payload["expires_display"] = timesince(now, invite.expires_at)
            active_invites.append(payload)
        else:
            payload["expires_display"] = timesince(invite.expires_at, now)
            expired_invites.append(payload)

    accepted_invite_count = invites_qs.filter(accepted_at__isnull=False).count()

    # --- Reservations across ALL restaurants owned by this user ---
    pending_reservations = []
    upcoming_reservations = []
    has_cancelled_upcoming = False

    tz = timezone.get_current_timezone()
    now_local = timezone.localtime()

    reservations_qs = (
        Reservation.objects.select_related("customer", "restaurant")
        .filter(restaurant__owner=request.user)
        .order_by("reservation_date", "reservation_time")
    )

    for reservation in reservations_qs:
        combined = datetime.datetime.combine(
            reservation.reservation_date, reservation.reservation_time
        )
        if timezone.is_naive(combined):
            reservation_dt = timezone.make_aware(combined, tz)
        else:
            reservation_dt = combined.astimezone(tz)

        guest_name = (
            (reservation.customer.get_full_name() or "").strip()
            or reservation.customer.email
        )

        payload = {
            "instance": reservation,
            "datetime": reservation_dt,
            "guest_name": guest_name,
            "guest_email": reservation.customer.email,
            "notes": reservation.notes,
            "restaurant_name": reservation.restaurant.name,
            "party_size": getattr(reservation, "party_size", None),
        }

        # Future pending reservations
        if (
            reservation.status == Reservation.Status.PENDING
            and reservation_dt >= now_local
        ):
            pending_reservations.append(payload)

        # Future confirmed or cancelled reservations → upcoming section
        elif (
            reservation.status
            in (Reservation.Status.CONFIRMED, Reservation.Status.CANCELLED)
            and reservation_dt >= now_local
        ):
            upcoming_reservations.append(payload)
            if reservation.status == Reservation.Status.CANCELLED:
                has_cancelled_upcoming = True

        # Past reservations are not needed anymore (no recent section)

    context = {
        "restaurant": restaurant,
        "has_restaurant": has_restaurant,
        "opening_hours_rows": opening_hours_rows,
        "active_invites": active_invites,
        "expired_invites": expired_invites[:3],
        "accepted_invite_count": accepted_invite_count,
        "invite_create_url": reverse("create_invitation"),
        "contact_support_url": reverse("contact_support"),
        "pending_reservations": pending_reservations,
        "upcoming_reservations": upcoming_reservations,
        "has_cancelled_upcoming": has_cancelled_upcoming,
        # Keep key for backwards compatibility; template can stop using it.
        "recent_reservations": [],
    }

    return render(request, "accounts/dashboard_owner.html", context)


@login_required
def staff_dashboard(request):
    if request.user.role != User.Roles.STAFF:
        return HttpResponseForbidden("403")
    return render(request, "accounts/dashboard_staff.html")


# --- Contact Support page ---
def contact_support(request):
    """
    Static Contact Support page (UI only for now).
    Later you can POST this form to send email/save a ticket.
    """
    return render(request, "accounts/contact_support.html")
