from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Full access — admin only."""
    message = "You do not have permission to perform this action. Admin role required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsAnalystOrAbove(BasePermission):
    """Read + analytics access — analyst and admin."""
    message = "You do not have permission to perform this action. Analyst role or above required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("analyst", "admin")
        )


class IsAnyAuthenticatedUser(BasePermission):
    """Any authenticated user regardless of role."""
    message = "Authentication credentials were not provided or are invalid."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)