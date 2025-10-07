from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.urls import reverse
from .models import User, StaffInvitation
from .forms import SignupForm, LoginForm

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
            messages.error(request, "Staff accounts are invite-only. Ask your manager for an invite link.")
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
            return render(request, "accounts/verify_prompt.html", {"email": user.email})
        else:
            return render(request, "accounts/signup.html", {"form": form}, status=400)
    form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})

def login_view(request):

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, 
                email=form.cleaned_data["email"], 
                password=form.cleaned_data["password"])
            if user is None:
                messages.error(request, "Invalid credentials.")
            else:
                if not user.is_email_verified:
                    return render(request, "accounts/verify_prompt.html", {"email": user.email})
                login(request, user); 
                return redirect("post_login")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

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
    user.is_email_verified = True; 
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

    if request.method == "POST":
        email = request.POST.get("email")
        inv = StaffInvitation.new_invite(email=email, invited_by=request.user)
        link = request.build_absolute_uri(reverse("accept_invite") + f"?token={inv.token}")
        send_mail(
            subject="Your Bookify staff invite",
             message= f"Open this link to join: {link}",
              from_email= None, 
              recepient_list=[email],
        )
        messages.success(request, f"Invitation sent to {email}")
        return redirect("owner_dashboard")
    return render(request, "accounts/create_invite.html")

def accept_invite_view(request):

    """Staff accepts invitation and sets a password."""

    token = request.GET.get("token") if request.method == "GET" else request.POST.get("token")
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
        if pwd and len(pwd) >= 8 and any(c.isalpha() for c in pwd) and any(c.isdigit() for c in pwd):
            user = User.objects.create_user(
                email=inv.email, 
                password=pwd, 
                role=User.Roles.STAFF, 
                is_email_verified=True,
            )
            inv.accepted_at = timezone.now(); 
            inv.save()
            messages.success(request, "Account created. You can log in.")
            return redirect("login")
        messages.error(request, "Password must be at least 8 chars, with letters and digits.")
    return render(request, "accounts/accept_invite.html", {"token": token})

@login_required
def customer_dashboard(request):
    if request.user.role != User.Roles.CUSTOMER: 
        return HttpResponseForbidden("403")
    return render(request, "accounts/dashboard_customer.html")

@login_required
def owner_dashboard(request):
    if request.user.role != User.Roles.OWNER: 
        return HttpResponseForbidden("403")
    return render(request, "accounts/dashboard_owner.html")

@login_required
def staff_dashboard(request):
    if request.user.role != User.Roles.STAFF: 
        return HttpResponseForbidden("403")
    return render(request, "accounts/dashboard_staff.html")
