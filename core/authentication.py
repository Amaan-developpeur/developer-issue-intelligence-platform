# core/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from core.models import ApiKey

class ApiKeyAuthentication(BaseAuthentication):
    """
    Authenticate requests with 'Authorization: ApiKey <token>'
    """
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("ApiKey "):
            return None  # Let other authenticators handle it

        key_value = auth_header.split(" ", 1)[1].strip()
        try:
            api_key = ApiKey.objects.get(key=key_value, is_active=True)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive API key")

        # Return (user, auth) — DRF expects a tuple.
        # We don't have a user, so we return None and the api_key object.
        return (None, api_key)
