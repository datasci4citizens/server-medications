from rest_framework import permissions

class IsPatient(permissions.BasePermission):
    """Common user: is_staff=False, is_superuser=False."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and not user.is_staff and not user.is_superuser
        )

class IsPharmacist(permissions.BasePermission):
    """Staff (pharmacist / health operator): is_staff=True, is_superuser=False."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and user.is_staff and not user.is_superuser
        )

class IsAdmin(permissions.BasePermission):
    """Admin: is_superuser=True, is_staff=True."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and user.is_superuser and user.is_staff
        )


class IsStaffOrAdmin(permissions.BasePermission):
    """Pharmacist or admin (any is_staff=True user)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)


class IsAuthenticatedReadOnlyOrAdminOrStaff(permissions.BasePermission):
    """Any authenticated user can read; only staff/admin can write."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return user.is_staff