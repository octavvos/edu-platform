from django.contrib import admin

from .models import Permission, Role, RoleAssignment


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("codename", "description")
    search_fields = ("codename",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    filter_horizontal = ("permissions",)


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "scope_type", "scope_id", "created_at")
    list_filter = ("scope_type", "role")
    search_fields = ("user__username",)
