from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if not email: return None
        try: user = User.objects.get(email=email)
        except User.DoesNotExist: return None
        return user if user.check_password(password) else None
