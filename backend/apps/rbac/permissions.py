from rest_framework.permissions import BasePermission

from .services import has_permission


def HasPermission(codename: str):
    """DRF permission factory: `permission_classes = [HasPermission("course.publish")]`."""

    class _HasPermission(BasePermission):
        def has_permission(self, request, view):
            return has_permission(request.user, codename)

    _HasPermission.__name__ = f"HasPermission[{codename}]"
    return _HasPermission
