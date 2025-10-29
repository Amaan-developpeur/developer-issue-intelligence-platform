# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

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
