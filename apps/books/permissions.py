from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Read-only access (GET, HEAD, OPTIONS) is allowed for anyone.
    Write access (POST, PUT, PATCH, DELETE) requires the user to have the ADMIN role.
    """
    message = 'Only admins can perform this action.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )
