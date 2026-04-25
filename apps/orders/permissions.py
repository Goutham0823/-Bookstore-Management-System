from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only users with the ADMIN role."""
    message = 'Only admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsCustomer(BasePermission):
    """Only users with the CUSTOMER role."""
    message = 'Only customers can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'CUSTOMER'
        )


class IsOrderOwnerOrAdmin(BasePermission):
    """Allow access to the order owner or any admin."""
    message = 'You do not have permission to access this order.'

    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == 'ADMIN'
            or obj.user == request.user
        )
