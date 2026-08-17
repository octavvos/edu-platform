from django.contrib import admin

from .models import AuditLog, FeatureFlag


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "object_type", "object_id", "ip_address", "created_at")
    list_filter = ("action", "object_type")
    search_fields = ("actor__username", "object_id")

    def has_change_permission(self, request, obj=None):
        return False  # append-only


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("key", "is_enabled", "description")
