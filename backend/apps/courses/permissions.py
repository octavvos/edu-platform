from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsTeacherOrReadOnly(BasePermission):
    """Anyone can read; only teachers/admins can create."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and (user.is_teacher or user.is_admin))

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None)
        return bool(request.user.is_admin or owner == request.user)
