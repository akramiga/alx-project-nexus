from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Authenticate using either email or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        try:
            # Try login with email first
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Fallback: try login with username
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        # Check the password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
