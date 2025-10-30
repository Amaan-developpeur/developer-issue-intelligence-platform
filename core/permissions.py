# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    """
    Allows full access to 'admin' role or staff users.
    Grants read-only (GET, HEAD, OPTIONS) to others.
    """

    def has_permission(self, request, view):
        user = request.user

        # --- Unauthenticated users: deny immediately
        if not user or not user.is_authenticated:
            return False

        # --- Admins (custom role or staff) get full access
        if getattr(user, "role", None) == "admin" or user.is_staff:
            return True

        # --- Everyone else: only read access
        return request.method in SAFE_METHODS
    

# core/permissions.py
from rest_framework.permissions import BasePermission

def HasScope(required_scope):
    """
    Returns a permission class that checks:
      - If an ApiKey is attached to request: required_scope must be in api_key.scopes
      - Otherwise: only allow authenticated admin users
    Use like: @permission_classes([HasScope("tasks:read")])
    """
    class HasScopePermission(BasePermission):
        def has_permission(self, request, view):
            api_key = getattr(request, "api_key", None)
            if api_key:
                # api_key.scopes is a list (JSONField)
                return api_key.is_active and (required_scope in (api_key.scopes or []))

            user = getattr(request, "user", None)
            return bool(user and user.is_authenticated and getattr(user, "role", "") == "admin")

    return HasScopePermission

