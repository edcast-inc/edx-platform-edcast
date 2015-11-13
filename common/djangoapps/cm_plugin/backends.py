from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailAuthBackend(ModelBackend):
    """Log in to Django without providing a password.
    """
    def authenticate(self, email=None):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
