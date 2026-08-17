from django.db.models import Q

from .models import Role, RoleAssignment


def has_permission(user, codename: str, *, scope_type: str = "global", scope_id=None) -> bool:
    """R-05: huquq tekshiruvi — API/queryset darajasida chaqiriladi."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    qs = RoleAssignment.objects.filter(user=user, role__permissions__codename=codename)
    if scope_type == "global":
        return qs.filter(scope_type=RoleAssignment.ScopeType.GLOBAL).exists()
    return qs.filter(
        Q(scope_type=RoleAssignment.ScopeType.GLOBAL)
        | Q(scope_type=scope_type, scope_id=scope_id)
    ).exists()


def assign_role(*, user, role_name: str, scope_type: str = "global", scope_id=None) -> RoleAssignment:
    role = Role.objects.get(name=role_name)
    assignment, _ = RoleAssignment.objects.get_or_create(
        user=user, role=role, scope_type=scope_type, scope_id=scope_id,
    )
    return assignment


def user_permission_codenames(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()
    return set(
        Role.objects.filter(assignments__user=user)
        .values_list("permissions__codename", flat=True)
        .exclude(permissions__codename__isnull=True)
    )
