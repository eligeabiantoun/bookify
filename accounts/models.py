from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.utils.crypto import get_random_string

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        if not email: raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password); user.save(using=self._db)
        return user
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    class Roles(models.TextChoices):
        CUSTOMER = "CUSTOMER","Customer"
        STAFF    = "STAFF","Staff"
        OWNER    = "OWNER","Owner"
        SUPPORT = "SUPPORT","Support"
    role = models.CharField(
        max_length=16, 
        choices=Roles.choices, 
        default=Roles.CUSTOMER)
    is_email_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def make_email_token(self) -> str:
        return TimestampSigner().sign(f"verify:{self.pk}")

    @staticmethod
    def verify_email_token(token: str, max_age=60*60*72):
        s = TimestampSigner()
        try:
            value = s.unsign(token, max_age=max_age)
            _, pk = value.split(":")
            return User.objects.get(pk=pk)
        except (BadSignature, SignatureExpired, ValueError, User.DoesNotExist):
            return None

class Restaurant(models.Model):
    name = models.CharField(max_length=255)

class StaffInvitation(models.Model):
    email = models.EmailField()
    restaurant = models.ForeignKey(Restaurant, null=True, blank=True, on_delete=models.SET_NULL)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invites")
    role = models.CharField(max_length=16, 
    choices=User.Roles.choices, 
    default=User.Roles.STAFF)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_token(): return get_random_string(48)

    @classmethod
    def new_invite(cls, *, email, invited_by, restaurant=None, days_valid=3):
        return cls.objects.create(
            email=email, restaurant=restaurant, token=cls.create_token(),
            invited_by=invited_by, expires_at=timezone.now()+timezone.timedelta(days=days_valid),
        )

    def is_valid(self): return self.accepted_at is None and timezone.now() < self.expires_at
